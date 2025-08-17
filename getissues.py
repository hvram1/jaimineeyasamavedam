import requests
import re
import os
import json

def fetch_open_issues(repo_owner, repo_name):
    """
    Fetch all open issues from a public GitHub repository.

    :param repo_owner: Owner of the repository
    :param repo_name: Name of the repository
    :return: List of open issues
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    comments_url_template = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{{issue_number}}/comments"
    params = {"state": "open"}
    headers = {"Accept": "application/vnd.github.v3+json"}
    # Use pagination to fetch all open issues
    all_issues = []
    page = 1
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            issues = response.json()
            if not issues:  # Break if no more issues
                break
            all_issues.extend(issues)
            page += 1
        else:
            print(f"Failed to fetch issues: {response.status_code}")
            return []
    all_issues.sort(key=lambda issue: issue['number'], reverse=False)
    return all_issues
    

# Example usage
if __name__ == "__main__":
    repo_owner = "hvram1"  # Replace with the repository owner's username
    repo_name = "jaimineeyasamavedam"  # Replace with the repository name
    issues_file = "issues.json"

    if os.path.exists(issues_file):
        with open(issues_file, "r") as file:
            open_issues = json.load(file)
    else:
        open_issues = fetch_open_issues(repo_owner, repo_name)
        with open(issues_file, "w") as file:
            json.dump(open_issues, file, indent=4)
    #open_issues = fetch_open_issues(repo_owner, repo_name)
    #json_format_list=[]
    section_hash={}
    
    subsection_number=0
    for issue in open_issues:
        to_json_hash={}
        json_format_hash={}
        issue_hash={}
        json_format_list=[]
        #print(f"Issue #{issue['number']}: {issue['title']}")
        #print(f"Text: {issue.get('body', 'No description provided')}")
        title=issue['title']
        if issue.get('body'):
            body_text = issue['body']
            body_text = body_text.replace('This is the current swara position . ','')
            body_text = body_text.replace('Please enter the new swara in the same format (i.e.) mantra(swara)mantramantra(swara) and log a correction','')
            lines=body_text.splitlines()
            #print(f"{title} ")
            for line in lines:
                    issue_hash={}
                    #print(f"Line {line}")
                    if not line.strip():
                        continue
                    text_to_process=line.strip()
                    # Extract swara string
                    swara_pattern = r'\(\s*(.*?)\s*\)'
                    
                    swara_matches = re.findall(swara_pattern, text_to_process)
                    swara_string = ' '.join(swara_matches)
                    swara_string = ' '.join(swara_matches).replace('  ', ' ')
                    # Remove swara and create mantra string
                    mantra_string = re.sub(swara_pattern, ' ', text_to_process).strip()
                    text_to_process=text_to_process.replace(')', ') ')
                    issue_hash['corrected-mantra']=text_to_process
                    issue_hash['corrected-swara']=swara_string
                    #print(f"Mantra String: {text_to_process}")
                    #print(f"Swara String: {swara_string}")
                    json_format_list.append(issue_hash)
            json_format_hash['corrected-mantra_sets']=json_format_list
            #title=title.replace('Issue in Swara Section ','')
            title=title.replace('Issue in Swara ','')
            #title_components = title.split()
            #print(title)
            title_components = title.split(',') # This should give you section=xx and subsection=yy
            section_name=title_components[0].split('=')[1]
            subsection_header_number = title_components[1].split('=')[1]
            # Ensure subsection_header_number is in the form 'subsection_N' where N is a number
            match = re.match(r'(subsection_\d+)', subsection_header_number)
            if match:
                subsection_header_number = match.group(1)
            #print(f"Section Name: {section_name}, Subsection Header Number: {subsection_header_number}")
            subsection_header = ' '.join(title_components[3:])
            json_format_hash['corrected-header']={'header_number':subsection_header_number,'header':subsection_header}
            #x='subsection_' + str(subsection_number)
            x=subsection_header_number
            json_format_hash[x] = json_format_list
            to_json_hash[x]=json_format_hash
            #subsection_number+=1
            if (section_hash.get(section_name)):
                my_hash=section_hash.get(section_name)['subsections']
                
                
            else:
                my_hash={}
            my_hash[x]=json_format_hash
            section_hash[section_name]={'subsections':my_hash}
            
            
    
    
    output_file = "output_text/corrected-Devanagari.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(section_hash, file, ensure_ascii=False, indent=4)