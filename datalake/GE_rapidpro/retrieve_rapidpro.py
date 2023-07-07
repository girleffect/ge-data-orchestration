from temba_client.v2 import TembaClient
import pandas as pd
from datetime import date, timedelta
import json

ISO_8601_DateTime_format = '%Y-%m-%dT%H:%M:%SZ'


def get_platform(urn):
    if urn.startswith("ext:"):
        return "website"
    elif urn.startswith("facebook:"):
        return "messenger"
    elif urn.startswith("whatsapp:"):
        return "whatsapp"
    elif urn.startswith("telegram:"):
        return "telegram"
    elif urn.startswith("tel:"):
        return "moya"
    else:
        return None


# No. Conversations Initiated
# No. Returning Users
def num_conversations_initiated_and_returning_users(client, chatbot):
    chatbot_name = chatbot["name"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    print(f"(contacts) num_conversations_initiated_and_returning_users yesterday ({yesterday}) for chatbot {chatbot_name}")

    df = pd.DataFrame()
    # https://rapidpro.ilhasoft.mobi/api/v2/contacts.json?before=2023-04-17&after=2023-04-16
    # for contact_batch in client.get_contacts(before=2023-04-17, after="2023-04-16").iterfetches(retry_on_rate_exceed=True):
    for contact_batch in client.get_contacts(before=today, after=yesterday).iterfetches(retry_on_rate_exceed=True):
        # df = df.append(pd.DataFrame([o.__dict__ for o in contact_batch]))  # https://stackoverflow.com/questions/34997174/how-to-convert-list-of-model-objects-to-pandas-dataframe
        df = df.append(pd.DataFrame([{"uuid": o.uuid, "created_on": o.created_on, "modified_on": o.modified_on, "last_seen_on": o.last_seen_on, "urn": o.urns[0]} for o in contact_batch]))
        # source code of rapidpro-python (for python 3.7) was updated in order to access last_seen_on

    if df.empty:
        print(f"Exiting because ZERO num_conversations_initiated_and_returning_users yesterday ({yesterday}) for chatbot {chatbot_name}.")
        return None
    else:
        # Create a platform column generated from the first urn of the contact
        df['platform'] = df['urn'].apply(get_platform)

    # # keep only the columns expected
    # columns_expected = ["uuid", "created_on", "last_seen_on", "modified_on", "platform", "urn"]
    # df = df.loc[:, columns_expected]

    # Save to csv file
    filename_csv = f"{yesterday}-{chatbot_name}-contacts.csv"
    df.to_csv(filename_csv, index=False, date_format=ISO_8601_DateTime_format)
    print(f"Saved file {filename_csv}")

    # for contact in contact_batch:
    #     print(contact.created_on)
    #     print(contact.__dict__)
    #     print(pd.DataFrame.from_dict(contact))


def num_onboarding_started(client, chatbot):
    chatbot_name = chatbot["name"]
    chatbot_start_flow = chatbot["start_flow"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    print(f"(runs) num_onboarding_started yesterday ({yesterday}) for chatbot {chatbot_name}")

    df = pd.DataFrame()
    for run_batch in client.get_runs(flow=chatbot_start_flow, before=today, after=yesterday).iterfetches(retry_on_rate_exceed=True):
        df = df.append(pd.DataFrame([{"id": o.uuid, "contact": o.contact.uuid, "created_on": o.created_on, "modified_on": o.modified_on} for o in run_batch]))  # https://stackoverflow.com/questions/34997174/how-to-convert-list-of-model-objects-to-pandas-dataframe

    if df.empty:
        print(f"Exiting because ZERO num_onboarding_started yesterday ({yesterday}) for chatbot {chatbot_name}.")
        return None

    # Save to csv file
    filename_csv = f"{yesterday}-{chatbot_name}-runs-onboarding.csv"
    df.to_csv(filename_csv, index=False, date_format=ISO_8601_DateTime_format)
    print(f"Saved file {filename_csv}")


def most_popular_flows(client, chatbot):
    chatbot_name = chatbot["name"]
    today = date.today()
    print(f"(flows) get list of flows (for most popular flows) for chatbot {chatbot_name}")

    df = pd.DataFrame()
    for run_batch in client.get_flows().iterfetches(retry_on_rate_exceed=True):
        df = df.append(pd.DataFrame([{"date": today, "uuid": flow.uuid, "name": flow.name, "archived": flow.archived, "active": flow.runs.active, "completed": flow.runs.completed, "interrupted": flow.runs.interrupted, "expired": flow.runs.expired, "total_runs": flow.runs.active + flow.runs.completed + flow.runs.interrupted + flow.runs.expired} for flow in run_batch]))  # https://stackoverflow.com/questions/34997174/how-to-convert-list-of-model-objects-to-pandas-dataframe

    if df.empty:
        print(f"Exiting because ZERO list of flows (for most popular flows) for chatbot {chatbot_name}.")
        return None
    else:
        df = df.sort_values(by=['total_runs'], ascending=False)
        # TODO filter out flows that are not important

    # Save to csv file
    filename_csv = f"{today}-{chatbot_name}-flows.csv"
    df.to_csv(filename_csv, index=False, date_format=ISO_8601_DateTime_format)
    print(f"Saved file {filename_csv}")


def get_uncaught_messages(client, chatbot):
    chatbot_name = chatbot["name"]
    chatbot_lookup_flow = chatbot["lookup_flow"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    print(f"(runs) uncaught_messages in lookup flow yesterday ({yesterday}) for chatbot {chatbot_name}")

    df = pd.DataFrame()
    for run_batch in client.get_runs(flow=chatbot_lookup_flow, before=today, after=yesterday).iterfetches(retry_on_rate_exceed=True):
        # https://stackoverflow.com/questions/34997174/how-to-convert-list-of-model-objects-to-pandas-dataframe
        df = df.append(pd.DataFrame([{"flow": o.flow.uuid, "flow name": o.flow.name, "run": o.uuid, "contact": o.contact.uuid, "created_on": o.created_on, "modified_on": o.modified_on, "uncaught_message": o.values["uncaught_message"].value} for o in run_batch]))

    if df.empty:
        print(f"Exiting because ZERO runs (lookup run) yesterday ({yesterday}) for chatbot {chatbot_name}.")
        return None

    # Save to csv file
    filename_csv = f"{yesterday}-{chatbot_name}-runs-uncaught_messages.csv"
    df.to_csv(filename_csv, index=False, date_format=ISO_8601_DateTime_format)
    print(f"Saved file {filename_csv}")


def get_values_quiz(quiz_values):
    return {k: v.value for (k, v) in quiz_values.items()}


def get_quizzes(client, chatbot):
    chatbot_name = chatbot["name"]
    chatbot_quiz_flows = chatbot["quiz_flows"]
    today = date.today()
    yesterday = today - timedelta(days=1)

    df = pd.DataFrame()
    for chatbot_quiz_flow in chatbot_quiz_flows:
        print(f"(runs) get quizzes yesterday ({yesterday}) for flow {chatbot_quiz_flow} and for chatbot {chatbot_name}")

        for run_batch in client.get_runs(flow=chatbot_quiz_flow, before=today, after=yesterday).iterfetches(retry_on_rate_exceed=True):
            # https://stackoverflow.com/questions/34997174/how-to-convert-list-of-model-objects-to-pandas-dataframe
            df = df.append(pd.DataFrame([{"flow": o.flow.uuid, "flow name": o.flow.name, "run": o.uuid, "contact": o.contact.uuid, "created_on": o.created_on, "modified_on": o.modified_on, "values": get_values_quiz(o.values), "exit_type": o.exit_type} for o in run_batch]))

    if df.empty:
        print(f"Exiting because ZERO runs (quizzes) yesterday ({yesterday}) for chatbot {chatbot_name}")
        return None

    # Save to csv file
    # filename_csv = f"{yesterday}-{chatbot_name}-runs-quizzes.csv"
    # df.to_csv(filename_csv, index=False, date_format=ISO_8601_DateTime_format)
    # print(f"Saved file {filename_csv}")

    # Save to json file
    filename_json = f"{yesterday}-{chatbot_name}-runs-quizzes.json"
    df.to_json(filename_json, orient="records", date_format="iso")
    print(f"Saved file {filename_json}")


def main():
    with open('auth.json', 'r') as f:
        chatbots = json.load(f)

    for chatbot_details in chatbots.values():
        rapidpro_client = TembaClient('rapidpro.ilhasoft.mobi', chatbot_details['token'])

        # No. Conversations Initiated
        # No. Returning Users
        num_conversations_initiated_and_returning_users(rapidpro_client, chatbot_details)

        # No. Onboarding Started flow
        num_onboarding_started(rapidpro_client, chatbot_details)

        # Most popular flows
        most_popular_flows(rapidpro_client, chatbot_details)

        # Uncaught messages
        get_uncaught_messages(rapidpro_client, chatbot_details)

        # Quizzes
        get_quizzes(rapidpro_client, chatbot_details)


if __name__ == "__main__":
    main()
