#!/usr/bin/env python3
import dateutil.parser as dp
import json
import os
import sys

import click
import requests

github_org = "myorg"
github_repo = "myrepo"
github_graphql_endpoint = "https://api.github.com/graphql"
github_deployment_endpoint = "https://api.github.com/repos/myorg/myrepo/deployments"


def get_latest_successful_deployment(github_api_token, stage):
    """get the latest successful/active deployment github sha"""
    # Assumption: One of the most recent 50 deployment attempts was successful
    query = """
    query($repo_owner:String!, $repo_name:String!, $deployment_env:String!) {
        repository(owner: $repo_owner, name: $repo_name) {
          deployments(environments: [$deployment_env], last: 50) {
            nodes {
              commitOid
              statuses(first: 100) {
                nodes {
                  state
                  updatedAt
                }
              }
            }
          }
        }
      }
      """

    variables = {"repo_owner": github_org, "repo_name": github_repo, "deployment_env": stage}

    headers = {"Authorization": "token %s" % github_api_token}
    query = {"query": query, "variables": variables}

    try:
        resp = requests.post(url=github_graphql_endpoint, json=query, headers=headers)
        if resp.status_code != 200:
            print("Error: Unexpected response {}".format(resp))
            print(resp.text)
            return None
    except requests.exceptions.RequestException as e:
        print("Error: {}".format(e))
        return None

    resp_json = json.loads(resp.text)
    deployments = resp_json["data"]["repository"]["deployments"]

    sha_tuple = (None, None)

    for node in deployments["nodes"]:
        gh_sha = node["commitOid"]
        for status in node["statuses"]["nodes"]:
            if status["state"] == "SUCCESS":
                parsed_t = dp.parse(status["updatedAt"])
                if sha_tuple[0] == None:
                    sha_tuple = (gh_sha, parsed_t)
                else:
                    if sha_tuple[1] < parsed_t:
                        sha_tuple = (gh_sha, parsed_t)
                break

    return sha_tuple


def trigger_deploy(github_api_token, deployment_stage, github_sha, dry_run):
    """Start deployment to the given environment based on the github sha"""
    headers = {"Authorization": "token %s" % github_api_token, "Accept": "application/vnd.github.v3.text-match+json"}

    tag = f"sha-{github_sha[0:8]}"

    params = {
        "ref": github_sha,
        "auto_merge": False,
        "environment": deployment_stage,
        "required_contexts": [],
        "payload": {"tag": tag},
    }

    if dry_run:
        print(f"Dry run requested. Would deploy {tag} to environment {deployment_stage}")
        return

    print(f"Deploying {tag} to environment {deployment_stage}")
    try:
        resp = requests.post(github_deployment_endpoint, headers=headers, json=params)
        if resp.status_code != 201:
            print("Error: Unexpected response {}".format(resp))
            print(resp.text)
            return
    except requests.exceptions.RequestException as e:
        print("Error: {}".format(e))
        return

    print("Deployment successful")

def validate_sha(ctx, param, value):
    if value is not None:
        if len(value) < 8:
            raise click.BadParameter("Github SHA must be at least 8 characters!")
    return value

@click.command()
@click.argument("deployment_stage")
@click.option("--github-sha", callback=validate_sha, help="github sha to be deployed", default=None)
@click.option("--dry-run", help="do not perform actual deployment", default=False, is_flag=True)
@click.option("--get-latest", help="get (short) github sha of latest successful deployment", default=False, is_flag=True)
def happy_deploy(deployment_stage, github_sha, dry_run, get_latest):
    api_token = os.getenv("GITHUB_TOKEN")
    if api_token is None:
        print("Error: Please set GITHUB_TOKEN environment variable")
        return

    read_deployment_stage = "staging"

    # If github sha is not provided, get the latest succesful deployment
    # github sha of staging environment
    if github_sha is None:
        github_sha, parsed_t = get_latest_successful_deployment(api_token, read_deployment_stage)
        if get_latest:
            print(github_sha[0:8])
            return
        print(f"Latest succesful '{read_deployment_stage}' deployment on {parsed_t}: commit {github_sha}")
    if github_sha is None:
        print(
            f"Error: Could not find a successful deployment for deployment stage {read_deployment_stage}, and no --github_sha was given"
        )
        sys.exit(1)

    # Trigger deployment on the given stage. This will trigger github actions
    # and start/update the deployment.
    if github_sha is not None:
        trigger_deploy(api_token, deployment_stage, github_sha, dry_run)


if __name__ == "__main__":
    happy_deploy()
