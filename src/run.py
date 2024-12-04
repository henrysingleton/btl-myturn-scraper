from scraper import build_output, get_session

session = get_session()
output = build_output(session)
for line in output:
    print(line)

