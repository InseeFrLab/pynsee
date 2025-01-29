from datetime import date
import logging
import re

import requests

from pynsee.utils.requests_session import PynseeAPISession

logger = logging.getLogger(__name__)


def _check_url(url):

    with PynseeAPISession() as session:

        try:
            check = session.get(url, stream=True, verify=False)
        except requests.exceptions.RequestException:
            pass
        else:
            return url

        logger.error(
            f"File not found on insee.fr:\n{url} - please open an issue on:\n"
            "https://github.com/InseeFrLab/pynsee"
        )

        try:
            list_string_split = url.split("/")
            filename = list_string_split[-1]

            list_potential_dates = []

            def get_close_dates_list(start_year, timespan=10):
                start_year = int(start_year)
                start_year_short = int(str(start_year)[-2:])

                list_close_year = (
                    list(range(start_year, start_year + timespan))
                    + list(range(start_year, start_year - timespan, -1))
                    + list(
                        range(start_year_short, start_year_short + timespan)
                    )
                    + list(
                        range(
                            start_year_short, start_year_short - timespan, -1
                        )
                    )
                )

                list_close_year = [str(y) for y in list_close_year]

                return list_close_year

            datefile = re.findall(r"2\d{3}|\d{2}", filename)[0]

            list_potential_dates += get_close_dates_list(datefile)

            current_year = date.today().year

            list_potential_dates += get_close_dates_list(current_year)
            list_potential_dates = list(dict.fromkeys(list_potential_dates))

            for d in list_potential_dates:
                filename2 = filename.replace(str(datefile), str(d))
                url2 = "/".join(
                    list_string_split[: (len(list_string_split) - 1)]
                    + [filename2]
                )
                try:
                    results = session.get(url2, stream=True, verify=False)
                except requests.exceptions.RequestException:
                    pass
                else:
                    break

                if d == list_potential_dates[-1]:
                    logger.warning("No other similar files have been found")
                    url2 = url
        except Exception:
            logger.error(
                "Error raised while trying to find another similar file"
            )

        if "url2" in locals():
            if url != url2:
                logger.warning(
                    f"The following file has been used instead:\n{url2}"
                )

        else:
            url2 = url

        return url2
