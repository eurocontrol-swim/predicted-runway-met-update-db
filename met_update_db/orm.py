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

from mongoengine import Document, DictField, DateTimeField, StringField, UUIDField, \
    ComplexDateTimeField


class Taf(Document):
    id = UUIDField(required=True, primary_key=True)
    airport_icao = StringField(required=True)
    content = DictField(required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    created_at = ComplexDateTimeField(required=True)

    meta = {
        'indexes': [
            'airport_icao',
            'start_time',
            'end_time',
            'created_at'
        ],
    }

    def __repr__(self):
        return f"<Taf: {self.airport_icao} | {self.created_at.isoformat()}>"

    def __str__(self):
        return self.__repr__()


class Metar(Document):
    id = UUIDField(required=True, primary_key=True)
    airport_icao = StringField(required=True)
    content = DictField(required=True)
    time = DateTimeField(required=True)
    created_at = ComplexDateTimeField(required=True)

    meta = {
        'indexes': [
            'airport_icao',
            # 'time',
            'created_at'
        ],
    }

    def __repr__(self):
        return f"<Metar: {self.airport_icao} | {self.created_at.isoformat()}>"

    def __str__(self):
        return self.__repr__()
