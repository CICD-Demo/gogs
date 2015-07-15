#!/bin/bash -e

cd $(dirname $0)

. utils
. ../../environment

HOSTNAME=gogs.$DOMAIN

oc create -f - <<EOF || true
kind: List
apiVersion: v1
items:
- kind: ReplicationController
  apiVersion: v1
  metadata:
    name: gogs
    labels:
      service: gogs
      function: infra
  spec:
    replicas: 1
    selector:
      service: gogs
      function: infra
    template:
      metadata:
        labels:
          service: gogs
          function: infra
      spec:
        containers:
        - name: gogs
          image: cicddemo/gogs:latest
          imagePullPolicy: IfNotPresent
          ports:
          - containerPort: 3000
          - containerPort: 22
            hostPort: 2222
          env:
          - name: GOGS_SERVER__ROOT_URL
            value: http://$HOSTNAME
          - name: GOGS_SERVER__DOMAIN
            value: $HOSTNAME
          - name: GOGS_SERVER__PROTOCOL
            value: http
          - name: GOGS_SERVER__SSH_PORT
            value: "2222"
          - name: GOGS_SERVER__OFFLINE_MODE
            value: "true"
          - name: GOGS_WEBHOOK__SKIP_TLS_VERIFY
            value: "true"
          securityContext:
            runAsUser: 0
        serviceAccount: root
      labels:
        service: gogs
        function: infra

- kind: Service
  apiVersion: v1
  metadata:
    name: gogs
    labels:
      service: gogs
      function: infra
  spec:
    ports:
    - port: 80
      targetPort: 3000
    selector:
      service: gogs
      function: infra

- kind: Route
  apiVersion: v1
  metadata:
    name: gogs
    labels:
      service: gogs
      function: infra
  spec:
    host: $HOSTNAME
    to:
      name: gogs
EOF

SVCIP=$(oc get services gogs -o template --template='{{.spec.portalIP}}')

while ! curl -fsm 1 -o /dev/null $SVCIP; do
  sleep 1
done

./install.py $SVCIP
SSH_IDENTITY=$HOME/.ssh/id_rsa_administrator ../../bin/push-gogs.sh
