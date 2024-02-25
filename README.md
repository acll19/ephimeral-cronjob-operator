# ephimeral-cronjob-operator

This is a sample operator built with [Kopf](https://kopf.readthedocs.io). Manages a Kubernetes custom resource called `EphimeralCronJob` which takes a cron expression and a number of times you want the job to run.

## Example

You can find an example in [ephimeralcronjob.example.yaml](ephimeralcronjob.example.yaml)

## Run it locally

You'll need a running Kubernetes cluster.

```bash
helm upgrade ephimeral-cronjob-operator --namespace kube-system \
oci://ghcr.io/acll19/charts/ephimeral-cronjob-operator \
--version 0.1.4
```

## Development

```bash
kopf run ephemeralcronjob.py --verbose
```

## Debugging operator

```bash
# list ecj
kubectl get ephimeralcronjob -n <namespace>  # or kubectl get ecj ...

# describe ecj
kubectl get ephimeralcronjob -n <namespace> <resource name>

# get events
kubectl get events -n <namespace>
```