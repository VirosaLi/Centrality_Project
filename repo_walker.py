import os
import json
import time

from npm_spider import import_package_dependencies


def import_repo_dependencies(repo_dir_name, output_name):
    """

    :param repo_dir_name: path to directory that hold all repos
    :param output_name: name for output file
    :return: the output data in dict format
    """
    json_dir = 'package.json'

    # walk through all downloaded repos and access their package.json file for their dependencies
    dep_dict = {}
    with os.scandir('repos') as it:

        for entry in it:
            if not entry.name.startswith('.') and not entry.is_file():
                json_path = os.path.join(repo_dir_name, entry.name, json_dir)
                if os.path.exists(json_path):
                    dep_list = []
                    with open(json_path, 'r') as json_file:
                        json_data = json.load(json_file)
                        if 'dependencies' in json_data:
                            for key, _ in json_data['dependencies'].items():
                                dep_list.append(key)
                            dep_dict[entry.name] = dep_list

    # sleep between requests to avoid "too many request" from npm server
    result_dict = {}
    for key, value in dep_dict.items():
        for package in value:
            package = f'/package/{package}'
            import_package_dependencies(package, result_dict, 5, 0)
            time.sleep(10)
        time.sleep(60)

    # dump dict to json
    j = json.dumps(result_dict)

    # write json to file
    f = open(output_name, "w")
    f.write(j)
    f.close()

    return result_dict


def main():
    base_dir = 'repos'
    output_name = 'dependencies_data_300.json'
    result = import_repo_dependencies(base_dir, output_name)

    # print out the result
    for key, value in result.items():
        print(key, value)


if __name__ == '__main__':
    main()
