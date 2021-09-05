"""The CLI for snapspam."""
import argparse
import json
import threading
from time import sleep
from typing import Callable


def start_threads(target: Callable, count: int):
    for i in range(count - 1):
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    # Instead of running n threads, run n - 1 and run one in the main thread
    target()


def main():
    """The main function to set up the CLI and run the spammers"""
    parser = argparse.ArgumentParser(
        description=
        'A CLI to spam multiple common anonymous message apps for Snapchat')

    subparsers = parser.add_subparsers(help='The app to spam',
                                       dest='target_app',
                                       required=True)

    ##### Sendit Parser #####
    sendit_parser = subparsers.add_parser('sendit',
                                          help='Spam a sendit sticker')
    sendit_parser.add_argument('sticker_id',
                               type=str,
                               help='The sticker ID or URL to spam')
    sendit_parser.add_argument('message', type=str, help='The message to spam')
    sendit_parser.add_argument('--msg-count',
                               type=int,
                               default=-1,
                               help='The amount of messages to send. '
                               'Set to -1 (default) to spam until stopped')
    sendit_parser.add_argument(
        '--thread-count',
        type=int,
        default=1,
        help='The amount of threads to create. Only valid for --msg-count -1. '
        'Note that the message count will NOT be divided between threads.')
    sendit_parser.add_argument(
        '--delay',
        type=int,
        default=500,
        help='Milliseconds to wait between message sends')
    sendit_parser.add_argument(
        '--sendit-delay',
        type=int,
        default=0,
        help='Minutes before the recipient gets the message '
        '(Part of sendit; not a custom feature)')

    ##### LMK Parser #####
    lmk_parser = subparsers.add_parser('lmk', help='Spam an LMK poll')

    lmk_parser.add_argument('lmk_id',
                            type=str,
                            help='The ID or URL of the poll to spam')
    lmk_parser.add_argument(
        'choice',
        type=str,
        help='The choice ID to send to the poll. '
        "If you don't know this, use get_choices as the argument")
    lmk_parser.add_argument('--msg-count',
                            type=int,
                            default=-1,
                            help='The amount of messages to send. '
                            'Set to -1 (default) to spam until stopped')
    lmk_parser.add_argument(
        '--thread-count',
        type=int,
        default=1,
        help='The amount of threads to create. Only valid for --msg-count -1. '
        'Note that the message count will NOT be divided between threads.')
    lmk_parser.add_argument('--delay',
                            type=int,
                            default=500,
                            help='Milliseconds to wait between message sends')

    args = parser.parse_args()

    if args.target_app == 'sendit':
        import sendit

        spammer = sendit.Sendit(args.sticker_id, args.message,
                                args.sendit_delay)

        def send():
            r = json.loads(spammer.post().content)
            if r['status'] == 'success':
                print('Sent message.')
            else:
                print(f'Message failed to send. Code: {r.status_code}')
                print(r.content)
            sleep(args.delay / 1000)

        if args.msg_count == -1:
            print('Sending messages until stopped.')
            print('(Stop with Ctrl + C)')
        else:
            print(f'Sending {args.msg_count} messages...')

        if args.msg_count == -1:

            def thread():
                while True:
                    send()

            start_threads(thread, args.thread_count)
        else:
            for _ in range(args.msg_count):
                send()
    elif args.target_app == 'lmk':
        import lmk

        spammer = lmk.LMK(args.lmk_id)

        # Scrape page for poll choices and print them
        if args.choice.lower() == 'get_choices':
            choices = spammer.get_choices()
            for choice in choices:
                print(f'ID: {choice.cid}')
                print('~' * (len(choice.cid) + 4))
                print(choice.contents)
                print('-' * 50)
            return

        def send(choice: str):
            r = spammer.post(choice)
            if r.status_code == 200:
                print('Sent message')
            else:
                print(f'Message failed to send. Code: {r.status_code}')
                print(r.content)
            sleep(args.delay / 1000)

        if args.msg_count == -1:
            print('Sending messages until stopped.')
            print('(Stop with Ctrl + C)')

            def thread():
                while True:
                    send(args.choice)

            start_threads(thread, args.thread_count)
        else:
            print(f'Sending {args.msg_count} messages...')
            for _ in range(args.msg_count):
                send()


if __name__ == '__main__':
    main()
