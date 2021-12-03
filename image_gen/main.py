import logging
from mkdocs.plugins import BasePlugin
import pandas as pd
from svgwrite import Drawing
from datetime import date, timedelta, time
from dateutil.relativedelta import relativedelta
from copy import deepcopy

alignment_color = "rgb(189, 120, 83)"
benefaction_color = "rgb(26, 44, 203)"
network_color = "rgb(227, 209, 43)"
robustness_color = "rgb(204, 32, 27)"
nan_color = "rgb(47,47,47)"

def create_svgs(data, today):
    starting_date = today - relativedelta(years=1)
    current_date = starting_date

    # Common for all diagrams
    if today.isoweekday() == 7:
        drw = Drawing(filename="main.svg", size=("935", "167"))
    else:
        drw = Drawing(filename="main.svg", size=("918", "167"))
    style = drw.style(
        ".user-contrib-text{font-size: 12px; fill: #b0b0b0;}svg{background-color:#1f1f1f}"
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
    aln_drw = deepcopy(drw)
    aln_drw.filename = "aln_drw.svg"
    bnf_drw = deepcopy(drw)
    bnf_drw.filename = "bnf_drw.svg"
    ntw_drw = deepcopy(drw)
    ntw_drw.filename = "ntw_drw.svg"
    rbs_drw = deepcopy(drw)
    rbs_drw.filename = "rbs_drw.svg"

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
    aln_week = aln_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    bnf_week = bnf_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    ntw_week = ntw_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
    rbs_week = rbs_drw.add(drw.g(class_="calendar_week", transform="translate(18,18)"))
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
        aln_week = aln_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        bnf_week = bnf_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        ntw_week = ntw_drw.add(
            drw.g(class_="calendar_week", transform=week_translation)
        )
        rbs_week = rbs_drw.add(
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
    aln_week = aln_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    bnf_week = bnf_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    ntw_week = ntw_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    rbs_week = rbs_drw.add(drw.g(class_="calendar_week", transform=week_translation))
    week_translation = "translate({},18)".format(last_ofset_short)
    week_short = drw_short.add(
        drw.g(class_="calendar_week", transform=week_translation)
    )
    aln_week_short = aln_drw_short.add(
        drw.g(class_="calendar_week", transform=week_translation)
    )
    bnf_week_short = bnf_drw_short.add(
        drw.g(class_="calendar_week", transform=week_translation)
    )
    ntw_week_short = ntw_drw_short.add(
        drw.g(class_="calendar_week", transform=week_translation)
    )
    rbs_week_short = rbs_drw_short.add(
        drw.g(class_="calendar_week", transform=week_translation)
    )
    for i in range(7):
        if i > today.isoweekday() or (today.isoweekday() == 7 and i > 0):
            continue
        draw_shape(
            campaign_tracker_data,
            current_date,
            i,
            drw,
            week,
            aln_week,
            bnf_week,
            ntw_week,
            rbs_week,
            warrior
        )
        draw_shape(
            campaign_tracker_data,
            current_date,
            i,
            drw_short,
            week_short,
            aln_week_short,
            bnf_week_short,
            ntw_week_short,
            rbs_week_short,
            warrior
        )
        current_date += timedelta(days=1)

    # Add month labels
    aln_drw.add(month)
    bnf_drw.add(month)
    ntw_drw.add(month)
    rbs_drw.add(month)

    aln_drw.save()
    bnf_drw.save()
    ntw_drw.save()
    rbs_drw.save()


def draw_shape(df, date_, i, drw_, aln_week_, bnf_week_, ntw_week_, rbs_week_):
    aln_desc = bnf_desc = ntw_desc = rbs_desc = "{}".format(date_.strftime("%B %d, %Y"))
    try:
        row = df.loc[[date_]]
        if row.iat[0, 0] is not None:
            aln_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=alignment_color)
        else:
            aln_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 1] is not None:
            bnf_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=benefaction_color)
        else:
            bnf_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 2] is not None:
            ntw_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=network_color)
        else:
            ntw_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=nan_color)
        if row.iat[0, 3] is not None:
            rbs_rect = drw_.rect(insert=(0, i * 17), size=(15, 15), fill=robustness_color)
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
    def on_page_content(self, html, page, config, site_navigation=None, **kwargs):

        match_iter = re.finditer(MATCH_REGEX, html)

        for match in match_iter:
            name = match.group('name')
            if name.startswith('meta.'):
                try:
                    meta_name = str(name.split('.')[1])
                    required_meta_data = str(page.meta[meta_name])
                    if not required_meta_data or not isinstance(required_meta_data, str):
                        logging.error('Unsupported meta data type. \
                                       Received %s : %s' % (meta_name, required_meta_data))
                        continue
                    html = html.replace(('{{ meta.%s }}' % meta_name), required_meta_data)

                except KeyError:
                    logging.error('Meta data not found: %s' % (meta_name))

        return html
