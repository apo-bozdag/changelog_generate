import os
import configparser
from datetime import datetime


class ChangelogGenerate:
    def __init__(self):
        self.config_file = 'config.ini'
        self.changelog_file = 'CHANGELOG.md'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        self.changelog_data = dict(added=[], removed=[], changed=[], fixed=[])

    def get_config_sections(self) -> list:
        """
        read config sections \n
        :return: list
        """
        return self.config.sections()

    @staticmethod
    def create_new_version(current_version: str) -> str:
        """
        create new version or blank \n
        :param current_version: str
        :return: str
        """
        try:
            left_v = str(current_version[:+1]) + "."
            right_v = str(format(float(current_version[-3:]) + 0.1, '.1f'))
            return left_v + right_v
        except ValueError:
            return ""

    @staticmethod
    def get_remote_url() -> str:
        """
        get git remote url \n
        :return: str
        """
        stream = os.popen("git config --get remote.origin.url")
        return stream.read().replace('.git', '/commit/')

    def latest_tag(self):
        stream = os.popen("git describe --long")
        g_tag = stream.read()
        if g_tag in 'fatal':
            self.create_git_tag()
        return g_tag.split('-')[0] if g_tag != '' and 'version/bin' not in g_tag else self.get_version()

    def create_git_tag(self):
        """
        create git tag \n
        :return:
        """
        os.popen(f'git tag -a -m "Tag for version {self.get_version()}" {self.get_version()}')

    def get_version(self) -> str:
        """
        get config.ini current version \n
        :return: str
        """
        if 'CHANGELOG' in self.config and 'version' in self.config['CHANGELOG']:
            return self.config['CHANGELOG']['version']
        else:
            return "1.0.0"

    def set_version(self, version: str):
        """
        set config.ini version \n
        :param version: str
        :return:
        """
        self.config['CHANGELOG'] = {
            "version": version
        }
        with open(self.config_file, 'w+') as configfile:
            self.config.write(configfile)

    @staticmethod
    def log_list_generate(log_item: str) -> dict:
        """
        single git log convert to dict \n
        :param log_item: str
        :return: dict
        """
        c_i_split = log_item.split('\n')
        if len(c_i_split) >= 2:
            message = c_i_split[0]
            sha = c_i_split[1]
            return {"sha": sha, "message": message}

    def get_logs(self) -> list:
        """
        get git logs \n
        :return: list
        """
        stream = os.popen(f'git log {self.latest_tag()}..HEAD --format=%B%H----DELIMITER----')
        commits = stream.read()
        commits_lists = map(self.log_list_generate, commits.split("----DELIMITER----\n"))
        return list(filter(lambda x: bool(x), commits_lists))

    def ready_changelog_data(self) -> dict:
        """
        ready self.changelog_data \n
        :return: dict
        """
        r_url = self.get_remote_url() if self.get_remote_url() else ''
        g_version = self.get_version()
        c_version = self.create_new_version(g_version)
        n_version = c_version if c_version else g_version
        s_version = f'(default new version: {n_version}) ' if c_version else c_version
        new_version = input(f'enter new version {s_version}(current: {g_version}): ') or n_version
        self.set_version(new_version)
        for log in self.get_logs():
            for key in self.changelog_data.keys():
                message = log['message']
                sha = log['sha']
                commit_url = f'([{sha[:+6]}]({r_url + sha}))'.replace('\n', '') if r_url else ''
                if message.startswith(key):
                    self.changelog_data[key].append(f'{message.replace(key + ": ", "")} {commit_url}')

        return self.changelog_data

    def run(self):
        change_logs = self.ready_changelog_data()
        new_change_log = f'# Version {self.get_version()} ({datetime.today().strftime("%Y-%m-%d")}) \n\n'
        for change_log in change_logs:
            if len(change_logs[change_log]):
                new_change_log += f'## {change_log}\n'
                for log_message in change_logs[change_log]:
                    new_change_log += f'* {log_message}\n'
                new_change_log += '\n'

        with open(self.changelog_file, 'r') as original:
            data = original.read()
        with open(self.changelog_file, 'w') as modified:
            modified.write(f"{new_change_log}\n" + data)

        self.create_git_tag()


if __name__ == '__main__':
    # test v2 için eklendi değişti
    # test v2 silindi diyelim fixlendi
    c_l_g = ChangelogGenerate()
    c_l_g.run()
