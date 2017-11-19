#!/usr/bin/env python
# Database access functions for the logs analysis.
#
import psycopg2


def db_execute(command):
    """
    Takes a SQL command as a string, then connects to the db 'news',
    executes the command, and returns the result, if any.

    >>> db_execute("SELECT id FROM authors LIMIT 1")
    [(1,)]
    """
    db = psycopg2.connect("dbname=news")
    db_cursor = db.cursor()
    db_cursor.execute(command)
    try:
        result = db_cursor.fetchall()
    except psycopg2.ProgrammingError:
        result = ""
    db.close()

    if result:
        return result


# Get posts from database.
def get_most_popular_articles():
    """
    Gets the top three most popular articles from the db,
    then prints it out in a pretty way.
    """
    top_articles = db_execute(
        """
        SELECT articles.title, page_views.views
        FROM articles, page_views
        WHERE articles.slug = page_views.slug
        LIMIT 3
        """)

    max_title_len = max(len(top_articles[0][0]),
                        len(top_articles[1][0]),
                        len(top_articles[2][0]))

    top_bot_of_table = (max_title_len + 13) * "-"
    post_titles_spaces = (max_title_len - 4) * " "
    title_spaces = ((max_title_len - 11) / 2) * " "
    title_col_dashes = (max_title_len + 2) * "-"

    # Print results
    print ("""
           {6}
           |{8} Most Popular Articles {8}|
           | Title{7}| Views  |
           |{9}+--------|
           | {0}{10} | {1} |
           | {2}{11} | {3} |
           | {4}{12} | {5} |
           {6}
           """.format(top_articles[0][0], top_articles[0][1],
                      top_articles[1][0], top_articles[1][1],
                      top_articles[2][0], top_articles[2][1],
                      top_bot_of_table,
                      post_titles_spaces,
                      title_spaces,
                      title_col_dashes,
                      (max_title_len - len(top_articles[0][0])) * " ",
                      (max_title_len - len(top_articles[1][0])) * " ",
                      (max_title_len - len(top_articles[2][0])) * " "
                      ))


def get_authors_by_popularity():
    """
    Gets all the authors, then lists them by number of views in a
    pretty way.
    """
    authors = db_execute(
        """
        SELECT authors.name, SUM(page_views.views) as views
        FROM authors, articles, page_views
        WHERE articles.slug = page_views.slug AND articles.author = authors.id
        GROUP BY authors.name
        ORDER BY views DESC
        """)

    name_lengths = []
    views_lengths = []
    for author in authors:
        name_lengths.append(len(author[0]))
        views_lengths.append(len(str(author[1])))

    max_authors_len = max(name_lengths)
    max_views_len = max(views_lengths)

    pre_row_spaces = " " * 11

    authors_to_return = ""
    for author in authors:
        post_name_spaces = " " * (max_authors_len - len(author[0]))
        post_views_spaces = " " * (max_views_len - len(str(author[1])))
        authors_to_return += "{0}| {1}{2} | {3}{4} |\n".format(
            pre_row_spaces,
            author[0],
            post_name_spaces,
            author[1],
            post_views_spaces)

    table_width = max_authors_len + max_views_len + 5
    top_bot_of_table = (table_width) * "-"
    post_authors_spaces = (max_authors_len - 7) * " "
    post_views_spaces = (max_views_len - 4) * " "
    sub_title_spaces = (table_width) * " "
    author_col_dashes = (max_authors_len + 2) * '-'
    views_col_dashes = (max_views_len + 2) * "-"
    title_spaces = (((max_authors_len - 11) / 2) * " ")

    print ("""
           -{0}-
           |{1} Most Authors Articles {1}|
           |{2}|
           | Authors {3}| Views{4}|
           |{5}+{6}|
           |{7}
           -{0}-
           """.format(top_bot_of_table,
                      title_spaces,
                      sub_title_spaces,
                      post_authors_spaces,
                      post_views_spaces,
                      author_col_dashes,
                      views_col_dashes,
                      authors_to_return[12:-1]))


def get_one_percent_error_days():
    """
    Gets the days when more than 1 percent of the requests resulted
    in errors, then prints the result in a pretty way.
    """
    days = db_execute(
        """
        SELECT
            TO_CHAR(errors_per_day.date, 'MONTHDD,YYYY') AS date,
            ROUND(
                errors_per_day.errors * 100.0 / total_logs_per_day.requests, 2)
                AS percent_errors
        FROM errors_per_day, total_logs_per_day
        WHERE
            errors_per_day.date = total_logs_per_day.date AND
            ROUND(errors_per_day.errors * 100.0 / total_logs_per_day.requests,
                  2) >= 1
        ORDER BY percent_errors DESC;
        """)

    date_lengths = []
    for day in days:
        date_lengths.append(len(day[0]))

    max_date_len = max(date_lengths)

    pre_row_spaces = " " * 11

    dates_to_return = ""
    for date in days:
        post_date_spaces = " " * (max_date_len - len(date[0]))
        dates_to_return += "{0}| {1}{2} |   {3}%  |\n".format(
            pre_row_spaces,
            date[0],
            post_date_spaces,
            date[1])

    table_width = max_date_len + 12
    top_bot_of_table = table_width * "-"
    post_date_spaces = (max_date_len - 3) * " "
    sub_title_spaces = (max_date_len + 12) * " "
    date_col_dashes = (max_date_len + 2) * '-'
    title_spaces = (((max_date_len - 9) / 2) * " ")

    print ("""
           -{0}--
           |{1}  Days with 1% Errors {1} |
           |{2} |
           | Date{3}| Percent  |
           |{4}+----------|
           {5}
           -{0}--
           """.format(top_bot_of_table,
                      title_spaces,
                      sub_title_spaces,
                      post_date_spaces,
                      date_col_dashes,
                      dates_to_return[11:-1]))

get_most_popular_articles()
get_authors_by_popularity()
get_one_percent_error_days()
