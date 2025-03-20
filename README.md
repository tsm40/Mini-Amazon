*This project was originally developed in 2022 as part of a full-stack development course. It was revisited and uploaded to GitHub in 2025 with documentation improvements and minor optimizations.*

This README provides a basic overview of how the app works / workflow.

## How App Works
There's two important overarching folders: `/app` and `/db`. 

`/app` is where you can find `/models`, `/templates`, and your python files that handle API calls (does stuff).
* `/models`: this is the code for the tables and the methods that can be used to interact with them. Each table is representing as a class whose attributes are the columns defined in `create.sql`. You update models of the corresponding table to update columns and add functionality (e.g., querying functions)
* `\templates`: this is the html code for the website pages. `base.html` is a parent that is the foundation that others can inherit from. All the other files correspond with their respective pages. 

`/db` has `/data`, `/generated`, `create.sql`, and `load.sql`. 
* `/data`: this is where the app pulls data from. You should put generated data here.
* `/generated`: this is where generated data is default placed
* `create.sql`: modify to create tables
* `load.sql`: modify to add created tables into a place where the frontend can interact with them. Follow existing code for template.

## An Example
* `Products` is defined in `create.sql`
* This table is loaded in `load.sql`
* This table has a model `product.py`
* This model has functions such as `get_all()` defined in `product.py`
* This model's functions are used in `index.py`
* `index.py` renders to the default webpage which has its info displayed via the definitions in `index.html`

## Workflow for Updating Tables
* Update tables in `create.sql`
* Make sure you have the proper loading code in `load.sql`
* Make sure the corresponding model is updated
* Run db/setup.sh
* If there are no errors your tables have been updated
