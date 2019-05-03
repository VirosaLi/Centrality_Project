from os import path
from subprocess import run

from github import Github


def github_repo_walker(query_word, star_limit, repos_path):
    """
    search github with given query word and star limit, clone all repos in the result to a directory

    :param query_word:
    :param star_limit:
    :param repos_path:
    """

    g = Github()
    repos = g.search_repositories(query_word, "stars", "desc")

    repos_dic = {}
    for repo in repos:
        if int(repo.stargazers_count) >= star_limit:
            repos_dic[repo.full_name] = repo.clone_url
        else:
            break

    # create a directory to store repos
    if not path.exists(repos_path):
        run(["mkdir", repos_path])

    # print(len(repos_dic))
    for repo_name, repo_url in repos_dic.items():

        # print(repo_name, repo_url)
        rp = repo_name.replace("/", "_")
        repo_path = "/".join((repos_path, rp))

        # create a directory to current repo
        if not path.exists(repo_path):
            run(["mkdir", repo_path])

        # clone the whole repo to path
        run(["git", "clone", repo_url, repo_path])


def main():
    query_word = "wallet+language:JavaScript"
    star_limit = 300
    repos_path = "repos"
    github_repo_walker(query_word, star_limit, repos_path)


if __name__ == '__main__':
    main()
