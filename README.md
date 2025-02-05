<!-- trunk-ignore-all(markdownlint/MD033) -->
<!-- trunk-ignore(markdownlint/MD041) -->
<div align="center">

  <img src=".github/resources/isotipo.png" height="180px" width="auto" alt="romm-muos logo">
    <h3 style="font-size: 25px;">
    A beautiful, powerful, muOS RomM client.
  </h3>

<br>

[![license-badge-img]][license-badge]
[![release-badge-img]][release-badge]
[![discord-badge-img]][discord-badge]

<!-- [![wiki-badge-img]][wiki] -->

  </div>
</div>

# Overview

[muOS](https://muos.dev/) app to connect to your RomM instance and fetch games directly to your handheld.

## Installation

1. [Download the repository as a zip file](https://github.com/rommapp/muos-app/archive/refs/heads/main.zip).
2. Extract the contents of the `muos-app-main.zip` file.
3. Navigate to the `muos-app-main/muos-app-main` directory.
4. Edit the `.env` file inside the `.romm` folder and add your RomM `host` (including protocol and port if needed, e.g., `http://my-romm-instance:8080`), `username`, and `password`.
5. Copy the `RomM.sh` file and the `.romm` folder to `/mnt/mmc/MUOS/application`.
6. Run the `RomM` application inside `muOS`.

## Support

If you have any issues with the app, please [open an issue](https://github.com/rommapp/muos-app/issues/new) in this repository. If the issue is with RomM itself, open an issue in the [RomM repository](https://github.com/rommapp/romm/issues/new/choose).

Join us on discord, where you can ask questions, submit ideas, get help, showcase your collection, and discuss RomM with other users.

[![discord-invite]][discord-invite-url]

<!-- Badges -->

[license-badge-img]: https://img.shields.io/github/license/rommapp/muos-app?style=for-the-badge&color=a32d2a
[license-badge]: LICENSE
[release-badge-img]: https://img.shields.io/github/v/release/muos-app/romm?style=for-the-badge
[release-badge]: https://github.com/rommapp/muos-app/releases
[discord-badge-img]: https://img.shields.io/badge/discord-7289da?style=for-the-badge
[discord-badge]: https://discord.gg/P5HtHnhUDH

<!-- Links -->

[discord-invite]: https://invidget.switchblade.xyz/P5HtHnhUDH
[discord-invite-url]: https://discord.gg/P5HtHnhUDH