import os
from numpy import random

from atproto import (
    CAR,
    AtUri,
    Client,
    FirehoseSubscribeReposClient,
    firehose_models,
    models,
    parse_subscribe_repos_message,
)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bluesky credentials
BLUESKY_USERNAME = "botsabedor.bsky.social"
BLUESKY_PASSWORD = f"${{ secrets.PASSWORD }}"
# Create a Bluesky client
client = Client("https://bsky.social")
firehose = FirehoseSubscribeReposClient()

respostas = ['ÓBVIO NÉ','Sim :)','SIM SIM SIM 3 VEZES SIM','Talvez, sla',
             'Vish, não sei hein...','Pensa mais um pouquinho','Não :/',
             'NEM FUDENDO','Nananinanão']

def process_operation(
    op: models.ComAtprotoSyncSubscribeRepos.RepoOp,
    car: CAR,
    commit: models.ComAtprotoSyncSubscribeRepos.Commit,
) -> None:
    uri = AtUri.from_str(f"at://{commit.repo}/{op.path}")

    if op.action == "create":
        if not op.cid:
            return

        record = car.blocks.get(op.cid)
        if not record:
            return

        record = {
            "uri": str(uri),
            "cid": str(op.cid),
            "author": commit.repo,
            **record,
        }
    

        if uri.collection == models.ids.AppBskyFeedPost:
        
            if f"@{BLUESKY_USERNAME}" in record["text"]:
                resposta = respostas[random.randint(len(respostas))]
                # send a reply to the post
                record_ref = {"uri": record["uri"], "cid": record["cid"]}
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=record_ref, root=record_ref
                )
                client.send_post(
                    reply_to=reply_ref,
                    text=resposta
                )


    if op.action == "delete":
        # Process delete(s)
        return

    if op.action == "update":
        # Process update(s)
        return

    return


# No need to edit this function - it processes messages from the firehose
def on_message_handler(message: firehose_models.MessageFrame) -> None:
    commit = parse_subscribe_repos_message(message)
    if not isinstance(
        commit, models.ComAtprotoSyncSubscribeRepos.Commit
    ) or not isinstance(commit.blocks, bytes):
        return

    car = CAR.from_bytes(commit.blocks)

    for op in commit.ops:
        process_operation(op, car, commit)


def main() -> None:
    client.login(BLUESKY_USERNAME, BLUESKY_PASSWORD)
    print("🤖bibibop to funcionando ")
    firehose.start(on_message_handler)


if __name__ == "__main__":
    main()
