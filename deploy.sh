#!/bin/bash -e

cd $(dirname $0)

. utils
. ../../environment

HOSTNAME=gogs.$DOMAIN

osc create -f - <<EOF || true
kind: List
apiVersion: v1beta3
items:
- kind: ReplicationController
  apiVersion: v1beta3
  metadata:
    name: gogs
    labels:
      component: gogs
  spec:
    replicas: 1
    selector:
      component: gogs
    template:
      metadata:
        labels:
          component: gogs
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
      labels:
        component: gogs

- kind: Service
  apiVersion: v1beta3
  metadata:
    name: gogs
    labels:
      component: gogs
  spec:
    ports:
    - port: 80
      targetPort: 3000
    selector:
      component: gogs

- kind: Route
  apiVersion: v1beta1
  metadata:
    name: gogs
    labels:
      component: gogs
  host: $HOSTNAME
  serviceName: gogs
EOF

SVCIP=$(osc get services gogs -o template --template='{{.spec.portalIP}}')

while ! curl -fsm 1 -o /dev/null $SVCIP; do
  sleep 1
done

./install.py $SVCIP
