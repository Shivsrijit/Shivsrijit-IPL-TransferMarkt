import click
from flask.cli import with_appcontext
from app.scraper import populate_database
from app import create_app

@click.command('scrape-ipl')
@with_appcontext
def scrape_ipl_command():
    """Scrape IPL data and populate the database."""
    app = create_app()
    with app.app_context():
        click.echo('Starting IPL data scraping...')
        populate_database()
        click.echo('Scraping completed!') 