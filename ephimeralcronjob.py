import os
import kopf
import kubernetes
import yaml
import time
import croniter


@kopf.on.create('ephimeralcronjob')
def create_fn(spec, name, namespace, logger, **kwargs):
    logger.info('Detected cronjob %s/%s, handling', namespace, name)
    if not spec.get('schedule'):
        raise kopf.PermanentError('Schedule is required')


@kopf.on.field('ephimeralcronjobs', field='spec.image')
def update_image_fn(old, new, status, namespace, logger, **kwargs):
    pass


@kopf.timer('ephimeralcronjobs', interval=30, initial_delay=2)
def trigger(spec, status, name, namespace, logger, **kwargs):
    if not spec.get('schedule'):
        raise kopf.PermanentError('Schedule is required')

    schedule = spec['schedule']
    now = time.time()
    cron = croniter.croniter(schedule, now)
    scheduled_next_run = cron.get_next()

    times = spec['times']
    if (status.get('trigger', None)):
        last_run = status['trigger'].get('last_run', None)
        next_run = status['trigger'].get('next_run', None)
        runs = status['trigger']['runs']

        if not last_run or (now >= next_run and runs < times):
            # create pod
            path = os.path.join(os.path.dirname(__file__),
                                'podtemplates/ephimeral.yaml')
            tmpl = open(path, 'rt').read()
            name_suffix = str(now).split('.')[1]
            text = tmpl.format(name=f"{name}-{name_suffix}",
                               image=spec['image'], command=spec['command'])
            data = yaml.safe_load(text)

            kopf.adopt(data)

            api = kubernetes.client.CoreV1Api()
            obj = api.create_namespaced_pod(
                namespace=namespace,
                body=data,
            )
            logger.info(f'Created pod {obj.metadata.name}')
            # end create pod
            return {
                'runs': runs+1,
                'last_run': now,
                'last_pod': obj.metadata.name,
                'next_run': scheduled_next_run,
            }

        return {
            'runs': runs,
            'last_run': last_run,
            'next_run': next_run,
            'last_pod': status['trigger']['last_pod'],
        }

    return {
        'runs': 0,
        'last_run': 0,
        'next_run': scheduled_next_run,
        'last_pod': '',
    }
