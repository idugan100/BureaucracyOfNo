# The Bureaucracy of No
This is a data science/visualization project that explores the word choice used by federal regulation when negating (saying no). I found it very interesting that different sections of Federal Regulation had different ratios of negation words.

## Project Structure
- analysis.py
    - This file uses the [eCRF API](https://www.ecfr.gov/developers/documentation/api/v1) to pull information about the titles and last update for each of the sections of [The Code of Federal Regulations](https://www.ecfr.gov/). It then pulls the latest version of each section and looks through the XML for a list of negation words. It keeps count for each section and a running total. If I run this code and push updated data to the github repo, the data on this site will stay current.
- output.json
    - analysis.py saves it's results in this file.
- index.html
    - this file ingests output.json and then used D3.js to create a filterable bar graph visualization.

Checkout the finished product [here](https://idugan100.github.io/BureaucracyOfNo/)!

