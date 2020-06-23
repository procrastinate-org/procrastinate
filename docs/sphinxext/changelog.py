from typing import Any, Dict, Iterable, List, Optional

import requests
from docutils import nodes
from docutils.parsers.rst import Directive, directives


class ChangelogDirective(Directive):

    # defines the parameter the directive expects
    # directives.unchanged means you get the raw value from RST
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {"github": directives.unchanged, "pypi": directives.unchanged}
    has_content = False
    add_index = False

    def run(self) -> Iterable[nodes.Node]:
        config = self.state.document.settings.env.config
        token = config.changelog_github_token
        if not token:
            # If we raise self.error here, that will keep people
            # from building the doc without a token. We don't want that.
            par = nodes.paragraph()
            par += nodes.Text("(Changelog not built because ")
            par += nodes.literal("", "changelog_github_token")
            par += nodes.Text(" parameter is missing in ")
            par += nodes.literal("", "conf.py")
            par += nodes.Text(")")
            return [par]

        owner_repo = self.extract_github_repo_name(self.options["github"])
        releases = self.extract_releases(owner_repo, token)

        pypi_name: Optional[str]
        try:
            pypi_name = self.extract_pypi_package_name(self.options["pypi"])
        except KeyError:
            pypi_name = None

        result_nodes: List[nodes.Node] = []
        for release in self.filter_releases(releases):
            result_nodes.extend(
                list(self.nodes_for_release(release, pypi_name=pypi_name))
            )

        return result_nodes

    def extract_github_repo_name(self, url: str) -> str:
        stripped_url = url.rstrip("/")
        prefix, postfix = "https://github.com/", "/releases"
        url_is_correct = stripped_url.startswith(prefix) and stripped_url.endswith(
            postfix
        )
        if not url_is_correct:
            raise self.error(
                "Changelog needs a Github releases URL "
                f"(https://github.com/:owner/:repo/releases). Received {url}"
            )

        return stripped_url[len(prefix) : -len(postfix)]

    def extract_pypi_package_name(self, url: str) -> str:
        stripped_url = url.rstrip("/")
        prefix = "https://pypi.org/project/"
        url_is_correct = stripped_url.startswith(prefix)
        if not url_is_correct:
            raise self.error(
                "Changelog needs a Github releases URL "
                f"(https://github.com/:owner/:repo/releases). Received {url}"
            )

        return stripped_url[len(prefix) :]  # noqa

    def filter_releases(self, releases: Iterable[Dict[str, Any]]):
        yield from (release for release in releases if not release["isDraft"])

    def nodes_for_release(
        self, release: Dict[str, Any], pypi_name: Optional[str] = None
    ) -> Iterable[nodes.Node]:

        tag = release["tagName"]
        title = release["name"]
        title = title if tag in title else f"{tag}: {title}"
        # Section
        id_section = nodes.make_id("release-" + tag)
        section = nodes.section(ids=[id_section])
        section += nodes.title(text=title)

        par = nodes.paragraph()

        # Links
        par += nodes.reference("", "GitHub", refuri=release["url"])
        if pypi_name:
            par += nodes.Text(" - ")
            url = "https://pypi.org/project/" f"{pypi_name}/{tag}/"
            par += nodes.reference("", "PyPI", refuri=url)

        section += par

        # Body
        section += nodes.raw(text=release["descriptionHTML"], format="html")
        yield section

    def extract_releases(self, owner_repo: str, token: str) -> Iterable[Dict[str, Any]]:
        session = requests.Session()

        # Necessary for GraphQL
        session.headers["Authorization"] = f"token {token}"
        owner, repo = owner_repo.split("/")
        query = """
        query {
            repository(owner: "%(owner)s", name: "%(repo)s") {
                releases(orderBy: {field: CREATED_AT, direction: DESC}, first:100) {
                    nodes {
                        name, descriptionHTML, url, tagName, isDraft
                    }
                }
            }
        }
        """ % {
            "owner": owner,
            "repo": repo,
        }
        query = query.replace("\n", "")

        url = "https://api.github.com/graphql"

        try:
            response = session.post(url, json={"query": query})
            response.raise_for_status()
            return response.json()["data"]["repository"]["releases"]["nodes"]
        except requests.HTTPError as exc:
            error = response.json()
            raise self.error(
                "Could not retrieve changelog from github: " + error["message"]
            ) from exc
        except requests.RequestException as exc:
            raise self.error(
                "Could not retrieve changelog from github: " + str(exc)
            ) from exc


def setup(app):
    app.add_config_value("changelog_github_token", None, "html")
    app.add_directive("changelog", ChangelogDirective)
