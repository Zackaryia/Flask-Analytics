from bs4 import BeautifulSoup



def insert_script_into_head(html_str, script_str):
    soup = BeautifulSoup(html_str, 'html.parser')

    head = soup.head

    if head == None:
        return html_str
    else:
        meta = soup.find('meta', property="run-analytics-js")
        if meta and meta['content'] == "no":
            return html_str

        script = soup.new_tag('script')
        script.string = script_str
        head.append(script)
        return str(soup)

if __name__ == "__main__":
    print(insert_script_into_head(b"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta property="run-analytics-js" content="no">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
            
    </body>
    </html>""", '<script>console.log("ok")</script>')) # Sould return the original string
