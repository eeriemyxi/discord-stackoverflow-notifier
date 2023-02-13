# Introduction
This is just a basic StackOverflow notifier that can send Discord webhooks to notify you. The webhook message is completely configurable using the `config.yml` file.

# Configuration
A sample configuration file is already provided in the repository, you may cheeck it out. `DATA` key is a [webhook message object](https://discord.com/developers/docs/resources/webhook#execute-webhook); you can customize it to your liking by reading the official documentation.

## Formatting
The syntax is as simple as `%(XXX)s` where `XXX` is the keyword name.
### Keywords
All available keywords can be seen [here](https://api.stackexchange.com/docs/questions#fromdate=2023-02-12&order=desc&max=2023-02-14&sort=creation&tagged=nim-lang&filter=default&site=stackoverflow&run=true): all the keys of each object of the `items` key is available as a keyword with slight modifications.
Heres a table on what I changed:
| `tags`       | Each tag has been comma separated followed by a space. |
|--------------|--------------------------------------------------------|
| `owner.link` | It can be retrieved by `author_link`                   |

And that's it for now.

# Usage
Clone the repository, install the requirements stated in `requirements.txt` by running `pip install -r requirements.txt`, edit the `config.yml` file, then simply run the project by doing `python .` in the directory.
