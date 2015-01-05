#!/usr/bin/python

class Jenkins():
    def ci_message(self, x):
        self.ci_message = x

        ci_msg = os.environ.get("CI_MESSAGE")
        data = json.loads(ci_msg)
        print(json.dumps(data, indent=4))

        with open('ci_message.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

        ci_msg_value = data[self.ci_message]
        return ci_msg_value
