#!/usr/bin/env python

# This script scrapes together statistics about the specified Cloud Foundry
# platform. The user of this script will need to specify 3 environment vars.
# - STATS_API_URL
# - STATS_USERNAME
# - STATS_PASSWORD
# It will print out the mean, median, max, and min for particular stats.
# This script currently gathers some per-org, per-user, and per-space stats.

import os # Reading env vars
import sys # Exiting with codes
import requests # Making http requests
import json # Parsing JSON payloads from http requests
from urlparse import urljoin # Joining urls together
import numpy # For statistics calculation

#################################
# Setup
#################################

# Read the API url.
api_url = os.getenv('STATS_API_URL', '')
if len(api_url) < 1:
    print 'Empty value for STATS_API_URL env var'
    sys.exit(1)

# Get the public info about the cloud foundry system
api_info_response = requests.get(urljoin(api_url, "/info"))
if api_info_response.status_code != 200:
    print 'Invalid response from API. Exiting..'
    sys.exit(1)

api_info_json = json.loads(api_info_response.text)
# Read the login url from the API info endpoint.
login_url = api_info_json['authorization_endpoint']

#################################
# Login
#################################

# Read the credentials for the user to get the stats.
username = os.getenv('STATS_USERNAME', '')
password = os.getenv('STATS_PASSWORD', '')

if len(username) < 1:
    print 'Empty value for STATS_USERNAME env var'
    sys.exit(1)

if len(password) < 1:
    print 'Empty value for STATS_PASSWORD env var'
    sys.exit(1)

# Construct request to get access token.
auth_request_headers = {
            'content-type':'application/x-www-form-urlencoded;charset=utf-8',
            'accept':'application/json;charset=utf-8',
            'authorization': 'Basic Y2Y6' # Same secret for CLI in CF's Github.
}

auth_request_body = {
                        'grant_type': 'password',
                        'username': username,
                        'password': password
}

# Make auth request
auth_response = requests.post(urljoin(login_url,'/oauth/token'),
                                headers=auth_request_headers,
                                data=auth_request_body)

# Fail if the response is not 200.
if auth_response.status_code != 200:
    print 'Invalid credentials. Exiting.'
    sys.exit(1)

# Parse the JSON.
auth_response_json = json.loads(auth_response.text)
# Get the access_token
access_token = auth_response_json['access_token']

#################################
# Helpers
#################################
# make_request makes an authenticated request to cloud foundry with a given
# access_token.
def make_request(path):
    request_header = {'Authorization': 'bearer ' + access_token}
    response = requests.get(urljoin(api_url, path),
                            headers=request_header)
    return response

# print_stats_on_data prints the average, max, min, median for a list of
# data points.
def print_stats_on_data(data_name, data):
    print ('%s\t\tAverage: %.2f\tMax: %.2f\tMin: %.2f\tMedian: %.2f' %
            (data_name, numpy.average(data), numpy.amax(data),
            numpy.amin(data), numpy.median(data)))

#################################
# Stat Gathering
#################################

#################################
# Per User Stats
#################################

# Total Users
total_users_response = make_request("/v2/users")
total_users_json = json.loads(total_users_response.text)
total_users_data = []
total_users_data.append(total_users_json['total_results'])
print_stats_on_data('Total Users', total_users_data)

# Spaces Per User
spaces_per_user_data = []
for user in total_users_json['resources']:
    spaces_response = make_request(user['entity']['spaces_url'])
    spaces_json = json.loads(spaces_response.text)
    spaces_per_user_data.append(spaces_json['total_results'])
print_stats_on_data('Spaces Per User', spaces_per_user_data)

# Orgs Per User
orgs_per_user_data = []
for user in total_users_json['resources']:
    orgs_response = make_request(user['entity']['organizations_url'])
    orgs_json = json.loads(orgs_response.text)
    orgs_per_user_data.append(orgs_json['total_results'])
print_stats_on_data('Orgs Per User', orgs_per_user_data)

#################################
# Per Space Stats
#################################

# Total Spaces
total_spaces_response = make_request("/v2/spaces")
total_spaces_json = json.loads(total_spaces_response.text)
total_spaces_data = []
total_spaces_data.append(total_spaces_json['total_results'])
print_stats_on_data('Total Spaces', total_spaces_data)

# Apps Per Space
apps_per_space_data = []
for space in total_spaces_json['resources']:
    apps_response = make_request(space['entity']['apps_url'])
    apps_json = json.loads(apps_response.text)
    apps_per_space_data.append(apps_json['total_results'])
print_stats_on_data('Apps Per Space', apps_per_space_data)

# Service Instances Per Space
svc_instances_per_space_data = []
for space in total_spaces_json['resources']:
    svc_instance_response= make_request(
                                    space['entity']['service_instances_url'])
    svc_instance_json = json.loads(svc_instance_response.text)
    svc_instances_per_space_data.append(svc_instance_json['total_results'])
print_stats_on_data('Svc Instances Per Space', svc_instances_per_space_data)

#################################
# Per Org Stats
#################################

# Total Orgs
total_org_response = make_request("/v2/organizations")
total_org_json = json.loads(total_org_response.text)
total_org_data = []
total_org_data.append(total_org_json['total_results'])
print_stats_on_data('Total Orgs', total_org_data)

# Spaces Per Org
spaces_per_org_data = []
for org in total_org_json['resources']:
    spaces_response = make_request(org['entity']['spaces_url'])
    spaces_json = json.loads(spaces_response.text)
    spaces_per_org_data.append(spaces_json['total_results'])
print_stats_on_data('Spaces Per Org', spaces_per_org_data)

# Users Per Org
users_per_org_data = []
for org in total_org_json['resources']:
    org_users_response = make_request(org['entity']['users_url'])
    org_users_json = json.loads(org_users_response.text)
    users_per_org_data.append(org_users_json['total_results'])
print_stats_on_data('Users Per Org', users_per_org_data)
