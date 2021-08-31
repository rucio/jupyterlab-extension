# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import html
import tornado
import rucio_jupyterlab.utils as utils
from .base import RucioHandler


template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Rule Not Found - Rucio JupyterLab Extension</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
  <style type="text/css">
  .content {
    max-width: 600px;
    margin: 0 auto;
    padding: 16px;
    margin-top: 24px;
  }
  .button {
    margin-top: 8px;
  }
  </style>
</head>
<body>
    <div class="content">
      <svg width="100px" viewBox="0 0 1779 453" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" xmlns:serif="http://www.serif.com/" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;stroke-miterlimit:2;">
          <g transform="matrix(1,0,0,1,-3188,-9151.54)">
              <g transform="matrix(4.16667,0,0,4.16667,4082.17,9382.56)">
                  <g transform="matrix(1,0,0,1,-297.64,-209.765)">
                      <path d="M237.05,194.69C237.05,180.103 226.987,172.807 206.86,172.8L182.59,172.8L182.59,246.88L202.59,246.88L202.59,219.88L207.66,219.88L223.37,246.88L246.06,246.88L224.49,214.6C232.87,209.913 237.057,203.277 237.05,194.69ZM206.35,204.87L202.6,204.87L202.6,188L206.6,188C213.46,188 216.89,190.55 216.89,195.65C216.857,201.797 213.343,204.87 206.35,204.87Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M295.78,216.17C295.78,221.503 294.857,225.347 293.01,227.7C291.163,230.053 288.2,231.227 284.12,231.22C280.307,231.22 277.42,230.037 275.46,227.67C273.5,225.303 272.52,221.503 272.52,216.27L272.52,172.8L252.41,172.8L252.41,217.8C252.41,227.487 255.12,234.917 260.54,240.09C265.96,245.263 273.72,247.847 283.82,247.84C294.16,247.84 302.073,245.173 307.56,239.84C313.047,234.507 315.79,227 315.79,217.32L315.79,172.8L295.79,172.8L295.78,216.17Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M364.33,188.15C367.318,188.127 370.29,188.572 373.14,189.47C375.943,190.374 378.685,191.456 381.35,192.71L387.48,177C380.307,173.543 372.442,171.758 364.48,171.78C357.8,171.615 351.196,173.234 345.35,176.47C339.944,179.581 335.6,184.252 332.89,189.87C329.922,196.157 328.456,203.049 328.61,210C328.61,222.26 331.59,231.633 337.55,238.12C343.51,244.607 352.08,247.85 363.26,247.85C370.47,247.972 377.625,246.575 384.26,243.75L384.26,226.86C381.23,228.122 378.136,229.223 374.99,230.16C371.896,231.071 368.686,231.529 365.46,231.52C354.62,231.52 349.2,224.393 349.2,210.14C349.2,203.293 350.533,197.917 353.2,194.01C355.621,190.243 359.854,188.014 364.33,188.15Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <rect x="398.68" y="172.8" width="20.11" height="74.07" style="fill:var(--jp-ui-font-color1);"/>
                      <path d="M495,181.31C488.92,174.863 479.983,171.64 468.19,171.64C456.397,171.64 447.437,174.89 441.31,181.39C435.15,187.89 432.07,197.307 432.07,209.64C432.07,222.1 435.17,231.59 441.37,238.11C447.57,244.63 456.477,247.89 468.09,247.89C479.883,247.89 488.833,244.647 494.94,238.16C501.047,231.673 504.107,222.2 504.12,209.74C504.12,197.247 501.08,187.77 495,181.31ZM479.37,226C476.923,229.48 473.163,231.22 468.09,231.22C458.13,231.22 453.15,224.06 453.15,209.74C453.15,195.28 458.15,188.05 468.15,188.05C473.083,188.05 476.79,189.817 479.27,193.35C481.75,196.883 482.993,202.347 483,209.74C483,217.1 481.79,222.52 479.37,226Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M164.12,233.55L164.12,242.81C164.115,243.788 163.308,244.59 162.33,244.59L96.24,244.59C95.264,244.59 94.46,243.786 94.46,242.81L91.16,242.81C91.165,245.595 93.455,247.885 96.24,247.89L162.33,247.89C165.115,247.885 167.405,245.595 167.41,242.81L167.41,230.59C166.513,231.779 165.396,232.784 164.12,233.55Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M164.12,176.72L164.12,213.52C165.401,214.298 166.518,215.316 167.41,216.52L167.41,176.72C167.405,173.935 165.115,171.645 162.33,171.64L125.18,171.64L125.18,174.93L162.33,174.93C163.312,174.93 164.12,175.738 164.12,176.72Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M162.92,215.14L154.52,210.3L145,204.79C139.786,201.786 133.026,203.589 130,208.79L111.2,241.3L136.65,241.3L146,225.13L149,226.85C150.396,230.665 154.047,233.217 158.109,233.217C163.431,233.217 167.809,228.838 167.809,223.517C167.809,220.072 165.975,216.877 163,215.14L162.92,215.14ZM143.56,210.31C144.272,209.069 145.598,208.301 147.029,208.301C149.223,208.301 151.029,210.107 151.029,212.301C151.029,214.496 149.223,216.301 147.029,216.301C146.323,216.301 145.63,216.114 145.02,215.76C143.129,214.662 142.472,212.206 143.56,210.31ZM165.93,228.08C164.312,230.883 161.312,232.615 158.075,232.615C154.269,232.615 150.849,230.218 149.55,226.64L149.47,226.43L149.27,226.31L146.27,224.59L149.01,219.85C149.12,219.66 149.23,219.46 149.32,219.27L154.19,210.84L162.59,215.68C166.903,218.169 168.41,223.762 165.93,228.08Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <circle cx="164.08" cy="223.16" r="1.7" style="fill:var(--jp-ui-font-color1);"/>
                      <path d="M110.09,238.4L107.4,236.85L108.96,234.15L111.65,235.71L110.09,238.4ZM113.2,233L110.51,231.45L112.07,228.76L114.76,230.31L113.2,233ZM116.31,227.62L113.62,226.06L115.18,223.37L117.87,224.93L116.31,227.62ZM119.42,222.23L116.73,220.68L118.28,217.99L120.98,219.54L119.42,222.23ZM122.53,216.85L119.84,215.29L121.39,212.6L124.09,214.16L122.53,216.85ZM125.64,211.46L123,209.92L124.55,207.23L127.25,208.78L125.64,211.46ZM128.74,206.29L126.25,204.43C126.93,203.509 127.708,202.664 128.57,201.91L130.62,204.24C129.922,204.858 129.291,205.548 128.74,206.3L128.74,206.29ZM146.21,202.7C145.404,202.235 144.553,201.853 143.67,201.56L144.67,198.61C145.757,198.963 146.804,199.432 147.79,200.01L146.21,202.7ZM132.89,202.63L131.36,199.92C132.359,199.363 133.411,198.907 134.5,198.56L135.44,201.56C134.556,201.835 133.702,202.197 132.89,202.64L132.89,202.63ZM141,201C140.076,200.9 139.144,200.9 138.22,201L137.91,197.9C139.047,197.78 140.193,197.78 141.33,197.9L141,201Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M111.56,181.07C111.454,180.947 111.396,180.79 111.396,180.627C111.396,180.254 111.703,179.947 112.076,179.947C112.135,179.947 112.193,179.955 112.25,179.97C120.411,181.977 126.373,189.084 126.93,197.47C126.931,197.484 126.931,197.499 126.931,197.513C126.931,197.887 126.624,198.193 126.251,198.193C126.05,198.193 125.859,198.104 125.73,197.95L111.56,181.07Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <path d="M96.6,189.58C96.469,189.503 96.319,189.463 96.167,189.463C95.695,189.463 95.307,189.851 95.307,190.323C95.307,190.442 95.332,190.561 95.38,190.67C99.674,200.429 109.871,206.314 120.47,205.15C120.902,205.1 121.232,204.73 121.232,204.296C121.232,203.988 121.067,203.703 120.8,203.55L96.6,189.58Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                      <circle cx="149.3" cy="212.22" r="1.7" style="fill:var(--jp-ui-font-color1);"/>
                      <path d="M166,228.18C162.98,228.18 159.967,227.899 157,227.34L156.7,228.91C159.388,229.422 162.114,229.71 164.85,229.77C165.296,229.295 165.691,228.776 166.03,228.22L166,228.18Z" style="fill:var(--jp-ui-font-color1);fill-rule:nonzero;"/>
                  </g>
              </g>
          </g>
      </svg>

      <h3>DID has no related replication rule</h3>
      <p>There is no replication rule belonging to the DID <code>{{ did }}</code> or the parent DIDs on RSE <code>{{ rse_name }}</code></p>
      <a href="{{ did_page_url }}">
        <button type="button" class="btn btn-primary button">View DID on Rucio WebUI</button>
      </a>
    </div>
</body>
</html>
"""


def render_rule_not_found_html(**kwargs):
    rendered = f"{template}"
    for key in kwargs:
        rendered = rendered.replace("{{ " + key + " }}", html.escape(kwargs[key]))
    return rendered


class OpenReplicationRuleHandler(RucioHandler):
    @tornado.web.authenticated
    def get(self):
        namespace = self.get_query_argument('namespace')
        did = self.get_query_argument('did')
        scope, name = did.split(':')

        rucio_instance = self.rucio.for_instance(namespace)
        mode = rucio_instance.instance_config.get('mode', 'replica')
        rucio_webui_url = rucio_instance.instance_config.get('rucio_webui_url')

        if not rucio_webui_url:
            self.set_status(500)
            self.finish("Rucio WebUI URL is not configured")
            return

        if mode != 'replica':
            self.set_status(400)
            self.finish("Extension is not in Replica mode")
            return

        replication_rule = self._resolve_did_replication_rule(rucio_instance, scope, name)
        if not replication_rule:
            self.set_status(404)
            did_page_url = f"{rucio_webui_url}/did?scope={scope}&name={name}"
            destination_rse = rucio_instance.instance_config.get('destination_rse')
            self.finish(render_rule_not_found_html(rse_name=destination_rse, did=scope + ":" + name, did_page_url=did_page_url))
            return

        rule_id, _ = replication_rule

        url = f"{rucio_webui_url}/rule?rule_id={rule_id}"
        self.redirect(url)

    def _resolve_did_replication_rule(self, rucio_instance, scope, name):
        replication_rule = self._fetch_replication_rule(rucio_instance, scope, name)

        if replication_rule is not None:
            return replication_rule

        parents = rucio_instance.get_parents(scope, name)
        if len(parents) == 0:
            return None

        for parent in parents:
            replication_rule = self._fetch_replication_rule(rucio_instance, scope=parent['scope'], name=parent['name'])
            if replication_rule is not None:
                return replication_rule

        return None

    def _fetch_replication_rule(self, rucio_instance, scope, name):
        destination_rse = rucio_instance.instance_config.get('destination_rse')

        rules = rucio_instance.get_rules(scope, name)
        filtered_rules = utils.filter(rules, lambda x, _: x['rse_expression'] == destination_rse)

        if len(filtered_rules) > 0:
            replication_rule = filtered_rules[0]
            rule_id = replication_rule.get('id')
            expires_at = replication_rule.get('expires_at')

            return rule_id, expires_at

        return None
