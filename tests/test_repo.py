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
from unittest import mock

import pytest

from met_update_db import repo, orm
from met_update_db.repo import WindInputSource, WindInput
from met_update_db.utils import datetime_from_string, datetime_from_string_with_ms


def get_current_timestamp():
    return int(datetime.datetime.utcnow().timestamp())


def test_add_taf(sample_taf_data):
    airport_icao = 'EHAM'
    repo.add_taf(taf_data=sample_taf_data, airport_icao=airport_icao)

    taf = orm.Taf.objects.all()
    assert taf.count() == 1
    assert taf[0].content == sample_taf_data
    assert taf[0].start_time == datetime_from_string(sample_taf_data['start_time']['dt'])
    assert taf[0].end_time == datetime_from_string(sample_taf_data['end_time']['dt'])
    assert taf[0].created_at == datetime_from_string_with_ms(sample_taf_data['meta']['timestamp'])


def test_add_metar(sample_metar_data):
    airport_icao = 'EHAM'
    repo.add_metar(metar_data=sample_metar_data, airport_icao=airport_icao)

    metar = orm.Metar.objects.all()
    assert metar.count() == 1
    assert metar[0].content == sample_metar_data
    assert metar[0].time == datetime_from_string(sample_metar_data['time']['dt'])
    assert metar[0].created_at == datetime_from_string_with_ms(sample_metar_data['meta']['timestamp'])


def test_get_taf__no_data__returns_none():
    assert repo.get_taf(airport_icao='EHAM', before_timestamp=get_current_timestamp()) is None


@pytest.mark.parametrize('taf', [
    [
        orm.Taf(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={'meta': {}},
            start_time=datetime.datetime(2022, 5, 30, 12),
            end_time=datetime.datetime(2022, 5, 30, 22),
            created_at=datetime.datetime(2022, 5, 30, 11)
        ),
        orm.Taf(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={'meta': {}},
            start_time=datetime.datetime(2022, 5, 31, 12),
            end_time=datetime.datetime(2022, 5, 31, 22),
            created_at=datetime.datetime(2022, 5, 31, 11)
        )
    ],
])
@pytest.mark.parametrize('airport_icao, before_timestamp', [
    (
        'EHAM',
        int(datetime.datetime(2022, 6, 1, 18).timestamp())
    ),
    (
        'EBBR',
        int(datetime.datetime(2022, 5, 30, 18).timestamp())
    )

])
def test_get_taf__data_exists__does_not_satisfy_query__returns_none(
        taf: list[orm.Taf], airport_icao, before_timestamp
):
    [t.save() for t in taf]

    assert repo.get_taf(airport_icao, before_timestamp) is None


@pytest.mark.parametrize('taf, before_timestamp', [
    (
        [
            orm.Taf(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                start_time=datetime.datetime(2022, 5, 30, 12),
                end_time=datetime.datetime(2022, 5, 30, 22),
                created_at=datetime.datetime(2022, 5, 30, 11)
            ),
            orm.Taf(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                start_time=datetime.datetime(2022, 5, 31, 12),
                end_time=datetime.datetime(2022, 5, 31, 22),
                created_at=datetime.datetime(2022, 5, 31, 11)
            )
        ],
        int(datetime.datetime(2022, 5, 30, 18).timestamp())
    )
])
def test_get_taf__data_exists__satisfies_the_query__returns_taf(
        taf: list[orm.Taf], before_timestamp
):
    [t.save() for t in taf]

    assert repo.get_taf(airport_icao='EHAM', before_timestamp=before_timestamp) == taf[0]


def test_get_metar__no_data__returns_none():
    assert repo.get_metar(airport_icao='EHAM', before_timestamp=get_current_timestamp()) is None


@pytest.mark.parametrize('metar', [
    [
        orm.Metar(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={'meta': {}},
            time=datetime.datetime(2022, 5, 30, 12),
            created_at=datetime.datetime(2022, 5, 30, 11)
        ),
        orm.Metar(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={'meta': {}},
            time=datetime.datetime(2022, 5, 31, 12),
            created_at=datetime.datetime(2022, 5, 31, 11)
        )
    ],
])
@pytest.mark.parametrize('airport_icao, before_timestamp', [
    (
        'EHAM',
        int(datetime.datetime(2022, 5, 30, 15).timestamp())
    ),
    (
        'EHAM',
        int(datetime.datetime(2022, 6, 1, 18).timestamp())
    ),
    (
        'EBBR',
        int(datetime.datetime(2022, 5, 30, 18).timestamp())
    )

])
def test_get_metar__data_exists__does_not_satisfy_query__returns_none(
        metar: list[orm.Metar], airport_icao, before_timestamp
):
    [t.save() for t in metar]

    assert repo.get_metar(airport_icao, before_timestamp) is None


@pytest.mark.parametrize('metar, before_timestamp', [
    (
        [
            orm.Metar(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                time=datetime.datetime(2022, 5, 30, 12),
                created_at=datetime.datetime(2022, 5, 30, 11)
            ),
            orm.Metar(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                time=datetime.datetime(2022, 5, 31, 12),
                created_at=datetime.datetime(2022, 5, 31, 11)
            )
        ],
        int(datetime.datetime(2022, 5, 30, 12, 30).timestamp())
    )
])
def test_get_metar__data_exists__satisfies_the_query__returns_metar(
        metar: list[orm.Metar], before_timestamp
):
    [t.save() for t in metar]

    assert repo.get_metar(airport_icao='EHAM', before_timestamp=before_timestamp) == metar[0]


@pytest.mark.parametrize('content, value_key, expected_value', [
    ({'key': {'value': 1}}, 'key', 1),
    ({'key': {'value': 1.2}}, 'key', 1.2),
    ({'key': {'val': 1.2}}, 'key', None),
    ({'key': {'value': 1}}, 'invalid_key', None),
    ({'key': {'value': 'invalid_value'}}, 'key', None),
    ({'key': {'value': None}}, 'key', None),
])
def test_taf_get_wind_value(content, value_key, expected_value):
    assert repo._get_wind_value(content, value_key) == expected_value


def test_get_metar_wind_input__no_metar_found__returns_none():
    assert repo.get_metar_wind_input('EHAM', before_timestamp=get_current_timestamp()) is None


@pytest.mark.parametrize('retrieved_metar, expected_wind_input', [
    (None, None),
    (
        orm.Metar(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={
                'wind_direction': {
                    'value': None
                },
                'wind_speed': {
                    'value': 10,
                }
            },
            time=datetime.datetime(2022, 5, 30, 12),
            created_at=datetime.datetime(2022, 5, 30, 11)
        ),
        None
    ),
    (
        orm.Metar(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={
                'wind_direction': {
                    'value': 180
                },
                'wind_speed': {
                    'value': None,
                }
            },
            time=datetime.datetime(2022, 5, 30, 12),
            created_at=datetime.datetime(2022, 5, 30, 11)
        ),
        None
    ),
    (
        orm.Metar(
            id=uuid.uuid4().hex,
            airport_icao='EHAM',
            content={
                'wind_direction': {
                    'value': 180
                },
                'wind_speed': {
                    'value': 10,
                }
            },
            time=datetime.datetime(2022, 5, 30, 12),
            created_at=datetime.datetime(2022, 5, 30, 11)
        ),
        WindInput(direction=180, speed=10)
    )
])
@mock.patch('met_update_db.repo.get_metar')
def test_get_metar_wind_input(mock_get_metar, retrieved_metar, expected_wind_input):
    mock_get_metar.return_value = retrieved_metar

    assert repo.get_metar_wind_input('EHAM', before_timestamp=get_current_timestamp()) \
           == expected_wind_input


@pytest.mark.parametrize('taf_content, before_timestamp, expected_backup_value', [
    (
        {
            'forecast': [
                {
                    'start_time': {'dt': '2022-03-19T07:00:00Z'},
                    'end_time': {'dt': '2022-03-19T09:00:00Z'},
                    'wind_speed': {'value': 1.1}
                },
                {
                    'start_time': {'dt': '2022-03-19T10:00:00Z'},
                    'end_time': {'dt': '2022-03-20T12:00:00Z'},
                    'wind_speed': {'value': None}
                }
            ]
        },
        int(datetime.datetime(2022, 3, 19, 8, 1, 40).timestamp()),
        1.1
    ),
    (
        {
            'forecast': [
                {
                    'start_time': {'dt': '2022-03-19T03:00:00Z'},
                    'end_time': {'dt': '2022-03-20T05:00:00Z'},
                    'wind_speed': {'value': None}
                },
                {
                    'start_time': {'dt': '2022-03-19T07:00:00Z'},
                    'end_time': {'dt': '2022-03-19T09:00:00Z'},
                    'wind_speed': {'value': 1.1}
                },
                {
                    'start_time': {'dt': '2022-03-19T10:00:00Z'},
                    'end_time': {'dt': '2022-03-20T12:00:00Z'},
                    'wind_speed': {'value': None}
                }
            ]
        },
        int(datetime.datetime(2022, 7, 13, 2, 48, 20).timestamp()),
        1.1
    )
])
def test_get_taf_wind_value__return_the_backup_value_in_case_none_is_found(
        taf_content, before_timestamp, expected_backup_value):
    assert repo._get_taf_wind_value(taf_content, before_timestamp, 'wind_speed') \
           == expected_backup_value


@mock.patch('met_update_db.repo.get_taf')
def test_get_taf_wind_input__no_metar_is_found__returns_none(mock_get_taf):
    mock_get_taf.return_value = None

    assert repo.get_taf_wind_input('EHAM', before_timestamp=get_current_timestamp()) is None


@pytest.mark.parametrize('wind_direction, wind_speed, expected_wind_input', [
    (None, None, None),
    (None, 10, None),
    (180, None, None),
    (180, 10, WindInput(direction=180, speed=10)),
])
@mock.patch('met_update_db.repo.get_taf')
@mock.patch('met_update_db.repo._get_taf_wind_speed')
@mock.patch('met_update_db.repo._get_taf_wind_direction')
def test_get_taf_wind_input(
        mock_get_taf_wind_direction,
        mock_get_taf_wind_speed,
        mock_get_taf,
        wind_direction,
        wind_speed,
        expected_wind_input
):
    mock_get_taf_wind_direction.return_value = wind_direction
    mock_get_taf_wind_speed.return_value = wind_speed
    mock_get_taf.return_value = mock.Mock()

    assert repo.get_taf_wind_input('EHAM', before_timestamp=get_current_timestamp()) \
           == expected_wind_input


@mock.patch('met_update_db.repo.get_taf_wind_input')
@mock.patch('met_update_db.repo.get_metar_wind_input')
def test_get_wind_input__no_data_available__raises_metnotavailable(
        mock_get_metar_wind_input,
        mock_get_taf_wind_input,
):
    mock_get_metar_wind_input.return_value = None
    mock_get_taf_wind_input.return_value = None

    with pytest.raises(repo.METNotAvailable):
        repo.get_wind_input('EHAM', before_timestamp=get_current_timestamp())


@pytest.mark.parametrize('metar_wind_input, taf_wind_input, expected_result', [
    (
        WindInput(direction=180, speed=10),
        None,
        (WindInput(direction=180, speed=10), WindInputSource.METAR)
     ),
    (
        WindInput(direction=180, speed=10),
        WindInput(direction=100, speed=8),
        (WindInput(direction=180, speed=10), WindInputSource.METAR)
    ),
    (
        None,
        WindInput(direction=180, speed=10),
        (WindInput(direction=180, speed=10), WindInputSource.TAF)
    ),
])
@mock.patch('met_update_db.repo.get_taf_wind_input')
@mock.patch('met_update_db.repo.get_metar_wind_input')
def test_get_wind_input(
        mock_get_metar_wind_input,
        mock_get_taf_wind_input,
        metar_wind_input,
        taf_wind_input,
        expected_result
):
    mock_get_metar_wind_input.return_value = metar_wind_input
    mock_get_taf_wind_input.return_value = taf_wind_input

    assert repo.get_wind_input('EHAM', before_timestamp=get_current_timestamp()) \
        == expected_result


def test_get_last_taf_end_time__no_taf_available__raises_metnotavailable():
    with pytest.raises(repo.METNotAvailable):
        repo.get_last_taf_end_time('EHAM')


@pytest.mark.parametrize('taf_objects, expected_last_taf_end_time', [
    (
        [
            orm.Taf(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                start_time=datetime.datetime(2022, 5, 30, 12),
                end_time=datetime.datetime(2022, 5, 30, 22),
                created_at=datetime.datetime(2022, 5, 30, 11)
            ),
            orm.Taf(
                id=uuid.uuid4().hex,
                airport_icao='EHAM',
                content={'meta': {}},
                start_time=datetime.datetime(2022, 6, 30, 12),
                end_time=datetime.datetime(2022, 6, 30, 22),
                created_at=datetime.datetime(2022, 6, 30, 11)
            ),
        ],
        datetime.datetime(2022, 6, 30, 22)
    )
])
def test_get_last_taf_end_time(taf_objects, expected_last_taf_end_time):
    [taf.save() for taf in taf_objects]

    assert repo.get_last_taf_end_time('EHAM') == expected_last_taf_end_time
