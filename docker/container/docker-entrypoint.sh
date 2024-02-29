#!/bin/bash
#eval "$(micromamba shell hook --shell bash)"
#micromamba activate base

# Step zero, get a compliant proxy. The key must NOT be group/other readable

if [[ -f ${X509_USER_KEY} ]] && [[ -f ${X509_USER_CERT} ]]
then
	KEY=$(mktemp)
	cat ${X509_USER_KEY} > "$KEY"
	xrdgsiproxy init -valid 9999:00 -cert ${X509_USER_CERT} -key "$KEY"
	rm -f "$KEY"
else
	echo "No certificate and/or key provided to create a proxy"
fi

exec "$@"
