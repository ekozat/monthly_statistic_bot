<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <img src="images/Squaredance.png" alt="Logo" width="80" height="80">

  <p align="center">
    Cloudflare Monthly Statistics report!
    <br />
    <a href="https://github.com/ekozat/monthly_statistic_bot/wiki"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ekozat/monthly_statistic_bot/issues">Report Bug</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://jumbleberry.com)

### Built With

This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

- [Python](https://www.python.org)
- [Pendulum](https://pendulum.eustace.io)
- virtualenv
- pip

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- Python3
- Pip
- Virtualenv

### Installation

```
# Create your virtual environment if it does not already exist

python -m virtualenv .env


# Activate your environment
source .env/bin/activate

# Install requirements
pip install -r requirements.txt
```

<!-- USAGE EXAMPLES -->

## Usage

Local Development and Testing

The following flag(s) are available when running this code:

- --testing

You can use them like so:

```
  python api.py --testing
  python api.py --no-testing
```

### Environment Variables

Provide the following for the script to execute:

```
URLSLACK - the slack webhook for sending the message to
xAuthKey - Your Cloudflare authentication key
xAuthEmail - Your Cloudflare email address that is paired with your authentication key
```

You can copy the `.env.sample` file to `.env` and substitue your values to have the script pick them up automatically.

_For more examples, please refer to the [Documentation](https://app.getguru.com/collections/furty/Engineering)_

<!-- CONTRIBUTING -->

## Contributing

### [Contribution](https://github.com/)

<!-- CONTACT -->

## Contact

[Emily Kozatchiner] - emily.kozatchiner@jumbleberry.com

[Alexander Hosking] - alexander.hosking@jumbleberry.com

<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

-

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/badge/Contributors-2-brightgreen?style=for-the-badge
[contributors-url]: https://github.com/ekozat/monthly_statistic_bot/graphs/contributors
[forks-shield]: https://img.shields.io/badge/Forks-0-blue?style=for-the-badge
[forks-url]: https://github.com/ekozat/monthly_statistic_bot/network/members
[stars-shield]: https://img.shields.io/badge/Stars-1-blue?style=for-the-badge
[stars-url]: https://github.com/ekozat/monthly_statistic_bot/stargazers
[issues-shield]: https://img.shields.io/badge/Issues-0-yessow?style=for-the-badge
[issues-url]: https://github.com/ekozat/monthly_statistic_bot/issues
[product-screenshot]: images/screenshot.png
