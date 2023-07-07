depending on the Python version, venv/Lib/site-packages/temba_client/v2/types.py should be modified.

- In `class Contact`, add the line `last_seen_on = DatetimeField()`
- In `class Run`, add the line `uuid = SimpleField()`

Generated files:
- `contacts.csv`: it contains the data for obtaining the metrics **No. Conversations Initiated** and **No. Returning Users**. There is a calculated column called `platform`.
- `runs-onboarding.csv`: it contains the data for obtaining the metric **No. Onboarding Started**. For retrieving the data, **one** `start_flow` MUST be set in the configuration file (`auth.json`).
- `flows.csv`: it contains the data for obtaining the metric **Most Popular Flows**. One extra column is added with the `requested date`.
- `runs-uncaught_messages.csv`: it contains the data for obtaining the metric **Uncaught Messages**. For retrieving the data, **one** `lookup_flow` MUST be set in the configuration file (`auth.json`).
- `runs-quizzes.json`: it contains the data for obtaining the metric **Quiz data**. For retrieving the data, **one or more** `quiz_flows` MUST be set in the configuration file (`auth.json`).
