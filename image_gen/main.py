import logging
from mkdocs.plugins import BasePlugin
import pandas as pd
from svgwrite import Drawing
from datetime import datetime, timedelta, time, timezone, date
from dateutil.relativedelta import relativedelta
from copy import deepcopy
from mkdocs.structure.files import File
import re

calibration_color = "rgb(138, 127, 91)"
condition_color = "rgb(150, 86, 31)"
connection_color = "rgb(25, 80, 105)"
contribution_color = "rgb(91, 83, 28)"
nan_color = "rgb(70, 73, 95)"

MATCH_REGEX = r"{{ svg-(?P<graph>contribution|calibration|connection|condition) }}"

def create_svgs(data, today):
    starting_date = today - relativedelta(years=1)
    current_date = starting_date

    # Common for all diagrams
    if today.isoweekday() == 7:
        drw = Drawing(filename="main.svg", size=("935", "167"))
    else:
        drw = Drawing(filename="main.svg", size=("918", "167"))
    style = drw.style(
        ".user-contrib-text{font-size: 12px; fill: #d0d0d0;}svg{background-color:rgba(0,0,0,0)}"
    )
    drw.defs.add(style)
    week = drw.g()
    week.add(
        drw.text("M", insert=(8, 46), class_="user-contrib-text", text_anchor="middle")
    )
    week.add(
        drw.text("W", insert=(8, 80), class_="user-contrib-text", text_anchor="middle")
    )
    week.add(
        drw.text("F", insert=(8, 114), class_="user-contrib-text", text_anchor="middle")
    )
    drw.add(week)

    # Create used diagrams
    clb_drw = deepcopy(drw)
    clb_drw.filename = "images/calibration.svg"
    cnd_drw = deepcopy(drw)
    cnd_drw.filename = "images/condition.svg"
    cnn_drw = deepcopy(drw)
    cnn_drw.filename = "images/connection.svg"
    cnt_drw = deepcopy(drw)
    cnt_drw.filename = "images/contribution.svg"

    # Create group for month labels
    month = drw.g()

    # Determin number of full weeks to display
    if starting_date.isoweekday() == 7:
        full_weeks = 52
        full_ofset = 18
        last_ofset = 902
    elif starting_date.isoweekday() == 6:
        full_weeks = 52
        full_ofset = 35
        last_ofset = 919
    else:
        full_weeks = 51
        full_ofset = 35
        last_ofset = 902

    # Add first week
    aln_week = clb_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    bnf_week = cnd_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    ntw_week = cnn_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    rbs_week = cnt_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    for i in range(7):
        if starting_date.isoweekday() == 7:
            continue
        if i < starting_date.isoweekday():
            continue
        draw_shape(
            data,
            current_date,
            i,
            drw,
            aln_week,
            bnf_week,
            ntw_week,
            rbs_week
        )
        current_date += timedelta(days=1)

    # Add main section of week
    week_num_short = 0
    for week_num in range(full_weeks):
        week_translation = "translate({},18)".format(week_num * 17 + full_ofset)
        week = drw.add(drw.g(class_="calendar_week", transform=week_translation))
        aln_week = clb_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        bnf_week = cnd_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        ntw_week = cnn_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        rbs_week = cnt_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        # Month stuff
        if week_num == 0:
            month.add(
                drw.text(
                    "{}".format(current_date.strftime("%b")),
                    insert=(week_num * 17 + full_ofset, 10),
                    class_="user-contrib-text",
                )
            )
        elif week_num == 2 and current_date.day < 20:
            month.add(
                drw.text(
                    "{}".format(current_date.strftime("%b")),
                    insert=(week_num * 17 + full_ofset, 10),
                    class_="user-contrib-text",
                )
            )
        elif current_date.day < 8 and week_num > 2:
            month.add(
                drw.text(
                    "{}".format(current_date.strftime("%b")),
                    insert=(week_num * 17 + full_ofset, 10),
                    class_="user-contrib-text",
                )
            )

        for i in range(7):
            draw_shape(
                data,
                current_date,
                i,
                drw,
                aln_week,
                bnf_week,
                ntw_week,
                rbs_week
            )
            current_date += timedelta(days=1)

    # Add last week
    week_translation = "translate({},18)".format(last_ofset)
    week = drw.add(drw.g(class_="calendar_week", transform=week_translation))
    aln_week = clb_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    bnf_week = cnd_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    ntw_week = cnn_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    rbs_week = cnt_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    for i in range(7):
        if i > today.isoweekday() or (today.isoweekday() == 7 and i > 0):
            continue
        draw_shape(
            data,
            current_date,
            i,
            drw,
            aln_week,
            bnf_week,
            ntw_week,
            rbs_week
        )
        current_date += timedelta(days=1)

    # Add month labels
    clb_drw.add(month)
    cnd_drw.add(month)
    cnn_drw.add(month)
    cnt_drw.add(month)

    clb_drw.save()
    cnd_drw.save()
    cnn_drw.save()
    cnt_drw.save()


def draw_shape(df, date_, i, drw_, aln_week_, bnf_week_, ntw_week_, rbs_week_):
    aln_desc = bnf_desc = ntw_desc = rbs_desc = "{}".format(date_.strftime("%B %d, %Y"))
    try:
        row = df.loc[[date_]]
        if row.iat[0, 0]:
            aln_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=calibration_color)
        else:
            aln_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 1]:
            bnf_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=condition_color)
        else:
            bnf_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 2]:
            ntw_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=connection_color)
        else:
            ntw_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 3]:
            rbs_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=contribution_color)
        else:
            rbs_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
    except KeyError:
        aln_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        bnf_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        ntw_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        rbs_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
    aln_rect.set_desc(aln_desc)
    aln_week_.add(aln_rect)
    bnf_rect.set_desc(bnf_desc)
    bnf_week_.add(bnf_rect)
    ntw_rect.set_desc(ntw_desc)
    ntw_week_.add(ntw_rect)
    rbs_rect.set_desc(rbs_desc)
    rbs_week_.add(rbs_rect)


class ImageGenPlugin(BasePlugin):
    def on_pre_build(self, config, **kwargs):
        df = pd.read_csv("log.csv", index_col="date", parse_dates=True)
        results = df.notna()
        tzinfo = timezone(timedelta(hours=-7.0))
        today = datetime.now(tzinfo).date()
        create_svgs(results, today)

    def on_files(self, files, config, **kwargs):
        calibration_file = File(
            path="calibration.svg",
            src_dir="images",
            dest_dir=config['site_dir'],
            use_directory_urls=False
        )
        files.append(calibration_file)
        condition_file = File(
            path="condition.svg",
            src_dir="images",
            dest_dir=config['site_dir'],
            use_directory_urls=False
        )
        files.append(condition_file)
        connection_file = File(
            path="connection.svg",
            src_dir="images",
            dest_dir=config['site_dir'],
            use_directory_urls=False
        )
        files.append(connection_file)
        contribution_file = File(
            path="contribution.svg",
            src_dir="images",
            dest_dir=config['site_dir'],
            use_directory_urls=False
        )
        files.append(contribution_file)
        return files

    def on_page_content(self, html, page, config, site_navigation=None, **kwargs):
        match_iter = re.finditer(MATCH_REGEX, html)

        for match in match_iter:
            graph = match.group('graph')
            if graph == "calibration":
                with open("images/calibration.svg", "r+") as svg:
                    html = html.replace(('{{{{ svg-{} }}}}'.format(graph)), svg.read())

            if graph == "condition":
                with open("images/condition.svg", "r+") as svg:
                    html = html.replace(('{{{{ svg-{} }}}}'.format(graph)), svg.read())

            if graph == "connection":
                with open("images/connection.svg", "r+") as svg:
                    html = html.replace(('{{{{ svg-{} }}}}'.format(graph)), svg.read())

            if graph == "contribution":
                with open("images/contribution.svg", "r+") as svg:
                    html = html.replace(('{{{{ svg-{} }}}}'.format(graph)), svg.read())

        return html
