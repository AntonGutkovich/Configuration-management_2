import csv
import requests
import xml.etree.ElementTree as ET
from termcolor import colored, cprint

version = "1.0"

def fetch_pom_file(package_name, repository_url):
    group_id, artifact_id, version = package_name.split(":")
    url = f"{repository_url}/{group_id.replace('.', '/')}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
    try:
        response = requests.get(url, timeout=30)
    except:
        return None
    if response.status_code == 200:
        return response.text
    else:
        return None

def parse_dependencies(pom_content):
    dependencies = []
    root = ET.fromstring(pom_content)
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
    for dependency in root.findall(".//m:dependency", namespaces=ns):
        group_id = dependency.find("m:groupId", namespaces=ns).text
        artifact_id = dependency.find("m:artifactId", namespaces=ns).text
        version_elem = dependency.find("m:version", namespaces=ns)
        version = version_elem.text if version_elem is not None else "unknown"
        dependencies.append(f"{group_id}:{artifact_id}:{version}")
    return dependencies

def get_dependencies(package_name, repository_url, visited=None):
    if visited is None:
        visited = set()
    dependencies = []
    if package_name in visited:
        return dependencies
    visited.add(package_name)
    pom_content = fetch_pom_file(package_name, repository_url)
    if pom_content:
        direct_dependencies = parse_dependencies(pom_content)
        dependencies.extend(direct_dependencies)
        for dep in direct_dependencies:
            dependencies.extend(get_dependencies(dep, repository_url, visited))
    return dependencies

def generate_plantuml_code(package_name, dependencies):
    plantuml_code = "@startuml\n"
    plantuml_code += f"[{package_name}] --> "
    separators = ""
    for dep in dependencies:
        plantuml_code += f"{separators}[{dep}]"
        separators = " --> "
    plantuml_code += "\n@enduml"
    return plantuml_code

def ultra_parser(package_name, repository_url, output_file):
    cprint("Processing...", "yellow", attrs=["bold"])
    dependencies = get_dependencies(package_name, repository_url)
    plantuml_code = generate_plantuml_code(package_name, dependencies)
    with open(output_file, 'w') as file:
        file.write(plantuml_code)
    print(plantuml_code)
    cprint("Done!", "green", attrs=["bold"])

def read_configuration(file_path):
    with open(file_path, mode='r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        for row in csv_reader:
            if len(row) == 3:
                yield row[0], row[1], row[2]

def main():
    print()

    config_file = "config.csv" 
    for path, package_name, output_file in read_configuration(config_file):
        ultra_parser(package_name=package_name, repository_url=path, output_file=output_file)

if __name__ == "__main__":
    main()

