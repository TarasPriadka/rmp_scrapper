# Rate My Professor Scrapper

## Description
Scrape info from Rate My Professors for your projects! This a project based on Scrapy which collects all of the data from the teacher's review pages such as their stats, and student comments.

## Deployment

### Setup your dataroot paths
```
python app/src/rmp/utils/general.py
```

### To start Flask server run the following (currently under construction):
```
cd web
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### UI:
To launch React webpage:
`npm start`

To deploy as a web extension:
`npm run build`
This will dump all of the files into `build` folder

Open your browser of preference and go to the settings where you can import extensions.
Import the build folder by selecting any file.
