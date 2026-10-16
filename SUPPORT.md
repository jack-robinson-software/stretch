# Support Stretch

A star, a useful bug report, a new movement idea or a contribution all help Stretch grow. You can also [buy Jack a coffee](https://www.buymeacoffee.com/jackrobinsonuk). Donations are always optional.

## Maintainer setup: Buy Me a Coffee

The current profile is **jackrobinsonuk**, linked from GitHub’s Sponsor button, the README and the app’s **Buy me a coffee…** menu item.

To change the profile, run from the repository root:

```sh
python3 scripts/configure_support.py YOUR_BUY_ME_A_COFFEE_PROFILE_URL
```

Pass the full HTTPS profile URL from your account. The script updates:

- `.github/FUNDING.yml`, which enables GitHub's Sponsor link;
- the Support section in `README.md`;
- the app's `StretchSupportURL` bundle setting, which enables **Buy me a coffee…** in the menu bar.

Then rebuild, check the destination, commit and push the changes:

```sh
./mac-app/build.sh
./mac-app/Stretch.app/Contents/MacOS/Stretch --self-test
```

The app opens the configured profile in the default browser only when the person selects it. It does not handle payments or collect payment information.

GitHub documents the funding-file format [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository).
