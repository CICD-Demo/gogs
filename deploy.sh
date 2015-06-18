#!/bin/bash -e

cd $(dirname $0)

. utils

. ../../environment

HOSTNAME=gogs.example.com

osc create -f - <<EOF
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
#        volumes:
#        - name: home
#          hostPath:
#            path: /vagrant/gogshome
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
#          - name: GOGS_DATABASE__DB_TYPE
#            value: mysql
#          - name: GOGS_DATABASE__HOST
#            value: gogs-mysql:3306
#          - name: GOGS_DATABASE__NAME
#            value: $GOGS_MYSQL_DATABASE
#          - name: GOGS_DATABASE__USER
#            value: $GOGS_MYSQL_USER
#          - name: GOGS_DATABASE__PASSWD
#            value: $GOGS_MYSQL_PASSWORD
#          volumeMounts:
#          - name: home
#            mountPath: /home/git
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
