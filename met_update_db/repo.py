"""
Copyright 2022 EUROCONTROL
==========================================

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
   and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of
conditions
   and the following disclaimer in the documentation and/or other materials provided with the
   distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to
endorse
   or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

==========================================

Editorial note: this license is an instance of the BSD license template as provided by the Open
Source Initiative: http://opensource.org/licenses/BSD-3-Clause

Details on EUROCONTROL: http://www.eurocontrol.int
"""

__author__ = "EUROCONTROL (SWIM)"

import datetime
import uuid
from dataclasses import dataclass
from enum import Enum

from mongoengine import Q

from met_update_db.orm import Taf, Metar
from met_update_db.utils import datetime_from_timestamp, datetime_from_string, \
    datetime_from_string_with_ms


class WindInputSource(Enum):
    METAR = 'METAR'
    TAF = 'TAF'


@dataclass
class WindInput:
    direction: float
    speed: float


def add_taf(taf_data: dict, airport_icao: str):
    taf = Taf(
        id=uuid.uuid4().hex,
        airport_icao=airport_icao,
        content=taf_data,
        start_time=datetime_from_string(taf_data['start_time']['dt']),
        end_time=datetime_from_string(taf_data['end_time']['dt']),
        created_at=datetime_from_string_with_ms(taf_data['meta']['timestamp'])
    )
    taf.save()


def add_metar(metar_data: dict, airport_icao: str):
    metar = Metar(
        id=uuid.uuid4().hex,
        airport_icao=airport_icao,
        content=metar_data,
        time=datetime_from_string(metar_data['time']['dt']),
        created_at=datetime_from_string_with_ms(metar_data['meta']['timestamp'])
    )
    metar.save()


def get_taf(airport_icao: str, before_timestamp: int) -> Taf | None:
    before_datetime = datetime_from_timestamp(before_timestamp)

    result = Taf.objects(
        Q(airport_icao=airport_icao)
        & Q(created_at__lte=before_datetime)
        & Q(start_time__lte=before_datetime)
        & Q(end_time__gte=before_datetime)
    ).order_by('-created_at')

    if result.count() == 0:
        return None

    return result[0]


def get_metar(airport_icao: str, before_timestamp: int) -> Metar | None:
    before_datetime = datetime_from_timestamp(before_timestamp)
    before_datetime_two_hours_ago = (before_datetime - datetime.timedelta(hours=2))

    result = Metar.objects(
        Q(airport_icao=airport_icao)
        & Q(created_at__lte=before_datetime)
        & Q(time__lte=before_datetime)
        & Q(time__gte=before_datetime_two_hours_ago)
    ).order_by('-created_at')

    if result.count() == 0:
        return None

    return result[0]


def _get_wind_value(content: dict, value_key: str) -> float | None:
    try:
        result = float(content[value_key]['value'])
    except (IndexError, KeyError, TypeError, ValueError):
        result = None

    return result


def get_metar_wind_input(airport_icao: str, before_timestamp: int) -> WindInput | None:

    metar = get_metar(airport_icao, before_timestamp)

    if not metar:
        return

    wind_direction = _get_wind_value(content=metar.content, value_key='wind_direction')

    if wind_direction is not None:
        wind_speed = _get_wind_value(content=metar.content, value_key='wind_speed')

        if wind_speed is not None:
            return WindInput(direction=wind_direction, speed=wind_speed)


def _get_taf_wind_value(taf_content: dict, before_timestamp: int, value_key: str) -> float | None:

    backup = None
    for forecast_item in taf_content['forecast']:
        wind_value = _get_wind_value(content=forecast_item, value_key=value_key)

        if wind_value is None:
            continue

        start_time_timestamp = datetime_from_string(forecast_item['start_time']['dt']).timestamp()
        end_time_timestamp = datetime_from_string(forecast_item['end_time']['dt']).timestamp()

        if start_time_timestamp <= before_timestamp <= end_time_timestamp:
            return wind_value

        backup = wind_value

    return backup


def _get_taf_wind_direction(taf: Taf, before_timestamp: int) -> float | None:
    return _get_taf_wind_value(taf.content, before_timestamp, value_key='wind_direction')


def _get_taf_wind_speed(taf: Taf, before_timestamp: int) -> float | None:
    return _get_taf_wind_value(taf.content, before_timestamp, value_key='wind_speed')


def get_taf_wind_input(airport_icao: str, before_timestamp: int) -> WindInput | None:

    taf = get_taf(airport_icao, before_timestamp)

    if not taf:
        return

    wind_direction = _get_taf_wind_direction(taf, before_timestamp)

    if wind_direction is not None:
        wind_speed = _get_taf_wind_speed(taf, before_timestamp)

        if wind_speed is not None:
            return WindInput(direction=wind_direction, speed=wind_speed)


def get_wind_input(airport_icao: str, before_timestamp: int) \
        -> tuple[WindInput, WindInputSource] | None:

    wind_input = get_metar_wind_input(airport_icao, before_timestamp)
    if wind_input is not None:
        return wind_input, WindInputSource.METAR

    wind_input = get_taf_wind_input(airport_icao, before_timestamp)
    if wind_input is not None:
        return wind_input, WindInputSource.TAF
