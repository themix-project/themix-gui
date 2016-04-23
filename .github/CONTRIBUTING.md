# Contributing to the Numix Project

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to the Numix Project and its visual works, which are hosted in the [Numix Project Organization](https://github.com/numixproject) on GitHub.
These are just guidelines, not rules, use your best judgment and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[What should I know before I get started?](#what-should-i-know-before-i-get-started)
  * [Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Style Guides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## What should I know before I get started?

### Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.
Please report unacceptable behavior to [numixproject@github.com](mailto:numixproject@github.com).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for a Numix product/project. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Please try not to deviate away from the predefined issue template's format as doing so will delay the review of your issue. 

#### Before Submitting A Bug Report

* **Most importantly**, check to see if you can reproduce the problem while using the latest version of the product/project from its [`master` branch](https://github.com/numixproject/numix-gtk-theme/tree/master).
* **Perform a [cursory search](https://github.com/issues?q=+is%3Aissue+user%3Anumixproject)** to see if the problem has already been reported. If it has, add a *thumbs up* reaction to the existing issue instead of opening a new one. Only add comments to issues when you have new information to provide that is relevant to the issue.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). After you've determined [which repository](http://github.com/numixproject) your bug is related to, create an issue on that repository and provide the following information.

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem. The **preferred format for issue titles** is:
  * `General Scope :: Specialized Scope :: One-sentence description of the issue`
    * Example: `GTK 3.20 :: Nautilus :: Active tab is not easily distinguishable from other tabs`
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and, when applicable, animated GIFs** which clearly demonstrate the problem. You can use [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) to create animated GIFs on Linux.

Provide more context by answering these questions when applicable:

* **Did the problem start happening recently** (e.g. after updating to a new version of the product) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version of the product?** What's the most recent version in which the problem doesn't happen? You can download older versions of the product from [its releases page](https://github.com/numixproject/).
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about your configuration and environment:

* **Which version of the product are you using?**
* **What's the name and version of the distribution you're using**?
* **Which version of GTK do you have installed?**

#### Template For Submitting Bug Reports

When you create a new issue, you will see that a structured template has been pre-filled for you. Please try not to deviate away from the template.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for a Numix product/project, including completely new features/designs and minor improvements to existing features/designs. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Try not to deviate away from the predefined issue template's format as doing so will delay the review of your issue.

#### Before Submitting An Enhancement Suggestion

* **Perform a [cursory search](https://github.com/issues?q=+is%3Aissue+user%3Anumixproject)** to see if the enhancement has already been suggested. If it has, add a *thumbs up* reaction to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). After you've determined [which repository](http://github.com/numixproject) your enhancement suggestions is related to, create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the problem. The **preferred format for issue titles** is:
  * `General Scope :: Specialized Scope :: One-sentence description of the suggested enhancement`
    * Example: `MATE Desktop :: Panel :: Add support for MATE Panel`
* **Provide a detailed description of the suggested enhancement**.
* **Include screenshots and, where applicable, animated GIFs** which help you demonstrate the current vs. desired results or to point out the part of the product/project to which the suggestion relates. You can use [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) to create animated GIFs on Linux.
* **Explain why this enhancement is needed**.
* **Specify which version of the product/project you're using.**.
* **Specify the name and version of the distribution you're using.**

#### Template For Submitting Enhancement Suggestions

When you create a new issue, you will see that a structured template has been pre-filled for you. Please try not to deviate away from the template.

### Your First Code Contribution

Unsure where to begin contributing to Numix? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues that should only require a few lines of code.
* [Help welcomed issues][help-welcomed] - issues that should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of *thumbs up* reactions which is a reasonable proxy for the impact a given change will have.

### Pull Requests

* Every pull request should directly address at least one existing github issue. All activity related to the review of a pull request will be tracked on the github issue targeted by the pull request including comments, questions, feedback, etc.
* If there is no existing github issue, you should create one prior to submitting your pull request.
* Your commit message should directly reference the issue it addresses ("Fix \#123" or "Fixes \#123").
* Pull requests should not include large scale changes. **Always** break up large scale changes into multiple pull requests.
* Since most Numix products/projects are visual design oriented, **always** include before/after screenshots and, when applicable, animated GIFs in your pull requests.
* Follow the [Sass](#sass-styleguide) and [CSS](https://github.com/styleguide/css) style guides.
* End files with a newline.

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Limit the first line to 72 characters or less
* Reference issues and other pull requests liberally

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests. Most labels are used across all Numix repositories, but some are specific to `numixproject/numix-gtk-theme`.

[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in. For example, you might be interested in [open issues across `numixproject/numix-gtk-theme` and all Numix products/projects which are labeled as bugs, but still need to be confirmed (reliably reproduced)](https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Abug+label%3Aneeds-confirmation) or perhaps [open pull requests in `numixproject/numix-gtk-theme` which haven't been reviewed yet](https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Apr+repo%3Anumixproject%2Fnumix-gtk-theme+comments%3A0). 

To help you find issues and pull requests, each label is listed with search links for finding open items with that label in `numixproject/numix-gtk-theme` only as well as across all Numix repositories. We encourage you to read about [other search filters](https://help.github.com/articles/searching-issues/) which will help you write more focused queries.

The labels are loosely grouped by their purpose, but it's not required that every issue have a label from every group nor that an issue can't have more than one label from the same group.

Please open an issue on numixproject/numix-gtk-theme if you have suggestions for new labels, and if you notice some labels are missing on some repositories, then please open an issue on that repository.

#### Type of Issue and Issue State

| Label name               | `numix-gtk-theme` :mag_right:                         | `numixproject`‑org :mag_right:                                 | Description                                                                                                                                   |
| ---                      | ---                                                                | ---                                                            | ---                                                                                                                                           |
| `enhancement`            | [search][search-numix-gtk-theme-repo-label-enhancement]            | [search][search-numixproject-org-label-enhancement]            | Feature requests.                                                                                                                             |
| `bug`                    | [search][search-numix-gtk-theme-repo-label-bug]                    | [search][search-numixproject-org-label-bug]                    | Confirmed bugs or reports that are very likely to be bugs.                                                                                    |
| `help-welcomed`          | [search][search-numix-gtk-theme-repo-label-help-welcomed]            | [search][search-numixproject-org-label-help-welcomed]        | The Nunmix Project core team would appreciate help from the community in resolving these issues.                                              |
| `beginner`               | [search][search-numix-gtk-theme-repo-label-beginner]               | [search][search-numixproject-org-label-beginner]               | Less complex issues which would be good first issues to work on for users who want to contribute to Numix.                                    |
| `needs-more-information` | [search][search-numix-gtk-theme-repo-label-needs-more-information] | [search][search-numixproject-org-label-needs-more-information] | More information needs to be collected about these problems or feature requests (e.g. steps to reproduce).                                    |
| `needs-confirmation`     | [search][search-numix-gtk-theme-repo-label-needs-confirmation]     | [search][search-numixproject-org-label-needs-confirmation]     | Likely bugs, but haven't been reliably reproduced.                                                                                            |
| `duplicate`              | [search][search-numix-gtk-theme-repo-label-duplicate]              | [search][search-numixproject-org-label-duplicate]              | Issues which are duplicates of other issues, i.e. they have been reported before.                                                             |
| `wontfix`                | [search][search-numix-gtk-theme-repo-label-wontfix]                | [search][search-numixproject-org-label-wontfix]                | The Numix Project core team has decided not to fix these issues for now, either because they're working as intended or for some other reason. |
| `invalid`                | [search][search-numix-gtk-theme-repo-label-invalid]                | [search][search-numixproject-org-label-invalid]                | Issues which aren't valid (e.g. user errors).                                                                                                 |

#### Topic Categories

| Label name        | `numix-gtk-theme` :mag_right:                  | `numixproject`‑org :mag_right:                          | Description                 |
| ---               | ---                                                         | ---                                                     | ---                         |
| `GTK`             | [search][search-numix-gtk-theme-repo-label-gtk]             | [search][search-numixproject-org-label-gtk]             | Related to GTK.             |
| `KDE`             | [search][search-numix-gtk-theme-repo-label-kde]             | [search][search-numixproject-org-label-kde]             | Related to KDE.             |
| `Xfce`            | [search][search-numix-gtk-theme-repo-label-xfce]            | [search][search-numixproject-org-label-xfce]            | Related to Xfce.            |
| `Openbox`         | [search][search-numix-gtk-theme-repo-label-openbox]         | [search][search-numixproject-org-label-openbox]         | Related to Openbox.         |
| `Unity`           | [search][search-numix-gtk-theme-repo-label-unity]           | [search][search-numixproject-org-label-unity]           | Related to Unity.           |
| `Cinnamon`        | [search][search-numix-gtk-theme-repo-label-cinnamon]        | [search][search-numixproject-org-label-cinnamon]        | Related to Cinnamon.        |
| `GNOME Shell`     | [search][search-numix-gtk-theme-repo-label-gnome-shell]     | [search][search-numixproject-org-label-gnome-shell]     | Related to GNOME Shell.     |
| `GTK 2.0`         | [search][search-numix-gtk-theme-repo-label-gtk-2.0]         | [search][search-numixproject-org-label-gtk-2.0]         | Related to GTK 2.0.         |
| `GTK 3.16`        | [search][search-numix-gtk-theme-repo-label-gtk-3.16]        | [search][search-numixproject-org-label-gtk-3.16]        | Related to GTK 3.16.        |
| `GTK 3.18`        | [search][search-numix-gtk-theme-repo-label-gtk-3.18]        | [search][search-numixproject-org-label-gtk-3.18]        | Related to GTK 3.18.        |
| `GTK 3.20`        | [search][search-numix-gtk-theme-repo-label-gtk-3.20]        | [search][search-numixproject-org-label-gtk-3.20]        | Related to GTK 3.20.        |
| `GTK 3.22`        | [search][search-numix-gtk-theme-repo-label-gtk-3.22]        | [search][search-numixproject-org-label-gtk-3.22]        | Related to GTK 3.22.        |
| `metacity/mutter` | [search][search-numix-gtk-theme-repo-label-metacity-mutter] | [search][search-numixproject-org-label-metacity-mutter] | Related to Metacity/Mutter. |

#### Pull Request Labels

| Label name         | `numix-gtk-theme` :mag_right:                   | `numixproject`‑org :mag_right:                           | Description
| ---                | ---                                                          | ---                                                      | ---                                                                                                                   |
| `work-in-progress` | [search][search-numix-gtk-theme-repo-label-work-in-progress] | [search][search-numixproject-org-label-work-in-progress] | Pull requests which are still being worked on, more changes will follow.                                              |
| `needs-review`     | [search][search-numix-gtk-theme-repo-label-needs-review]     | [search][search-numixproject-org-label-needs-review]     | Pull requests which need code review, and approval from maintainers or Numix Project core team.                       |
| `acknowledged`     | [search][search-numix-gtk-theme-repo-label-acknowledged]     | [search][search-numixproject-org-label-acknowledged]     | Pull requests that have been acknowledged/claimed by a maintainer or Numix Project core team member for later review. |
| `under-review`     | [search][search-numix-gtk-theme-repo-label-under-review]     | [search][search-numixproject-org-label-under-review]     | Pull requests being reviewed by maintainers or Numix Project core team.                                               |
| `requires-changes` | [search][search-numix-gtk-theme-repo-label-requires-changes] | [search][search-numixproject-org-label-requires-changes] | Pull requests which need to be updated based on review comments and then reviewed again.                              |
| `needs-testing`    | [search][search-numix-gtk-theme-repo-label-needs-testing]    | [search][search-numixproject-org-label-needs-testing]    | Pull requests which need manual testing.                                                                              |


[search-numix-gtk-theme-repo-label-enhancement]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aenhancement
[search-numixproject-org-label-enhancement]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aenhancement
[search-numix-gtk-theme-repo-label-bug]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Abug
[search-numixproject-org-label-bug]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Abug
[search-numix-gtk-theme-repo-label-help-welcomed]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Ahelp-welcomed
[search-numixproject-org-label-help-welcomed]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Ahelp-welcomed
[search-numix-gtk-theme-repo-label-beginner]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Abeginner
[search-numixproject-org-label-beginner]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Abeginner
[search-numix-gtk-theme-repo-label-needs-more-information]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aneeds-more-information
[search-numixproject-org-label-needs-more-information]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aneeds-more-information
[search-numix-gtk-theme-repo-label-needs-confirmation]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aneeds-confirmation
[search-numixproject-org-label-needs-confirmation]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aneeds-confirmation
[search-numix-gtk-theme-repo-label-duplicate]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aduplicate
[search-numixproject-org-label-duplicate]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aduplicate
[search-numix-gtk-theme-repo-label-wontfix]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Awontfix
[search-numixproject-org-label-wontfix]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Awontfix
[search-numix-gtk-theme-repo-label-invalid]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Ainvalid
[search-numixproject-org-label-invalid]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Ainvalid

[search-numix-gtk-theme-repo-label-gtk]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk             
[search-numixproject-org-label-gtk]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk                         
[search-numix-gtk-theme-repo-label-kde]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Akde            
[search-numixproject-org-label-kde]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Akde                       
[search-numix-gtk-theme-repo-label-xfce]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Axfce           
[search-numixproject-org-label-xfce]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Axfce                       
[search-numix-gtk-theme-repo-label-openbox]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aopenbox        
[search-numixproject-org-label-openbox]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aopenbox                   
[search-numix-gtk-theme-repo-label-unity]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aunity         
[search-numixproject-org-label-unity]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aunity                       
[search-numix-gtk-theme-repo-label-cinnamon]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Acinnamon      
[search-numixproject-org-label-cinnamon]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Acinnamon                  
[search-numix-gtk-theme-repo-label-gnome-shell]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agnome-shell     
[search-numixproject-org-label-gnome-shell]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agnome-shell                  
[search-numix-gtk-theme-repo-label-gtk-2.0]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk-2.0       
[search-numixproject-org-label-gtk-2.0]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk-2.0
[search-numix-gtk-theme-repo-label-gtk-3.16]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk-3.16
[search-numixproject-org-label-gtk-3.16]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk-3.16
[search-numix-gtk-theme-repo-label-gtk-3.18]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk-3.18
[search-numixproject-org-label-gtk-3.18]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk-3.18
[search-numix-gtk-theme-repo-label-gtk-3.20]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk-3.20
[search-numixproject-org-label-gtk-3.20]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk-3.20
[search-numix-gtk-theme-repo-label-gtk-3.22]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Agtk-3.22
[search-numixproject-org-label-gtk-3.22]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Agtk-3.22
[search-numix-gtk-theme-repo-label-metacity-mutter]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Ametacity-mutter
[search-numixproject-org-label-metacity-mutter]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Ametacity-mutter
[search-numix-gtk-theme-repo-label-work-in-progress]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Awork-in-progress
[search-numixproject-org-label-work-in-progress]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Awork-in-progress
[search-numix-gtk-theme-repo-label-needs-review]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aneeds-review
[search-numixproject-org-label-needs-review]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aneeds-review
[search-numix-gtk-theme-repo-label-acknowledged]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aacknowledged
[search-numixproject-org-label-acknowledged]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aacknowledged
[search-numix-gtk-theme-repo-label-under-review]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aunder-review
[search-numixproject-org-label-under-review]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aunder-review
[search-numix-gtk-theme-repo-label-requires-changes]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Arequires-changes
[search-numixproject-org-label-requires-changes]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Arequires-changes
[search-numix-gtk-theme-repo-label-needs-testing]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Anumixproject%2Fnumix-gtk-theme+label%3Aneeds-testing
[search-numixproject-org-label-needs-testing]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Anumixproject+label%3Aneeds-testing

[beginner]:https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abeginner+label%3Ahelp-wanted+user%3Anumixproject+sort%3Acomments-desc
[help-wanted]:https://github.com/issues?q=is%3Aopen+is%3Aissue+label%3Ahelp-wanted+user%3Anumixproject+sort%3Acomments-desc
