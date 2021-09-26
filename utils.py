import os


def read_requirements():
    requirement_paths = [
        'requirements.txt',
        *[os.path.join('fxmodes', fxmode, 'requirements.txt') for fxmode in os.listdir('fxmodes')]
    ]

    requirements = {}

    for requirement_path in requirement_paths:
        try:
            with open(requirement_path, 'r') as file:
                for line in file.readlines():
                    requirement, version = line.split('==')
                    version = version.strip()

                    existing_requirement = requirements.get(requirement)
                    if existing_requirement:
                        print('')
                        print(f'Warning: conflicting requirement "{requirement}"')
                        print(f'It\'s been specified in "{requirement_path}" with version "{version}"')
                        print(f'But also somewhere else with version "{version}"')
                        print('Make sure that all fxmodes are up-to-date or manually correct the versions')
                        print('')
                    else:
                        requirements[requirement] = version

        except FileNotFoundError:
            pass

        except ValueError:
            print('')
            print(f'{requirement_path} contains an invalid entry.')
            print('make sure that all requirements have a set version (e.g. numpy==1.21.2)')
            print('')

    return requirements


def read_pip_freeze():
    requirements = {}
    output = os.popen('pip freeze').read()

    if output:
        for line in output.split('\n'):
            try:
                requirement, version = line.split('==')
                version = version.strip()
                requirements[requirement] = version
            except ValueError:
                pass

    return requirements


def manage_requirements():
    print('Checking requirements...')
    installed_packages = read_pip_freeze()
    mismatched_packages = {}
    for requirement, version in read_requirements().items():
        pip_package_version = installed_packages.get(requirement)
        if pip_package_version:
            if not pip_package_version == version:
                print(f'Package "{requirement}" is installed in version {pip_package_version} but {version} is needed')
                mismatched_packages[requirement] = version
        else:
            print(f'Package "{requirement}" is needed in version {version} but not installed yet')
            mismatched_packages[requirement] = version

    if mismatched_packages:
        print()
        print('Do you want to install the packages? [Y/n]')
        choice = input()

        while not choice.lower() in ('y', 'n', ''):
            print('Invalid choice, try again.')
            choice = input()

        # TODO handle invalid input properly
        if choice.lower() in ('y', ''):
            packages = ' '.join([f'{requirement}=={version}' for requirement, version in mismatched_packages.items()])
            exit_code = os.system(f'pip install {packages}')

            print('')
            if exit_code == 0:
                print('Installation successful! ImmersiveFX will now exit.')
                print('Start it again so the changes take effect.')
            else:
                print('Installation *not* successful... ImmersiveFX will now exit.')
                print('Start it again to retry.')
            exit(exit_code)
        else:
            pass
