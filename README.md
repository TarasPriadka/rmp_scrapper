# Rate My Professor Scrapper

## Description:
Scrape info from Rate My Professors for your projects! This a project based on Scrapy which collects all of the data from the teacher's review pages such as their stats, and student comments.

## How to use:

### Initial Setup:
    Setup a location for your data root with `export DATAROOT=~/rmp_scrapper`
    Run `python src/rmp/utils/misc.py`. This will prepare data root for scraping.

    Optional: edit `$DATAROOT/scraping/scrape_input.json`. You should edit `college_sid` and `names`. 
    - Obtain `college_sid` from RMP urls. EX: go to the rmp search and search for a teacher in your school. URL will be something like `https://www.ratemyprofessors.com/search/teachers?query=PROF_NAME&sid=SID`. Enter SID in the url in the config file.
    - Scraper will search for `names` in RMP and scrape all of the search results. So if you want to scrape all of the the teachers with the name `John` and `Julie`, edit `names` to contain strings `"John"` and `"Julie"`.


### Scraper:
    Go to `src/rmp/scraper/`. Run 
    ```
    scrapy crawl rmp -a db_file="teachers_new.db" -a input_file="scrape_input.json"
    ```

    This will save all of the scraped teachers in the `$DATAROOT/db/teachers_new.db`. 

### Using DB:
    
    Use db with
    ```
    from rmp.utils.sqlite.database import SqlConnector

    sql = SqlConnector('PATHTODB', 'TABLENAME')
    print(sql.get_all_profesors())
    ```
    
