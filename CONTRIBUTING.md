# Getting Started
## Fork the repository on GitHub.

Clone your forked repository to your local machine:

    git clone https://github.com/Boavizta/e-footprint.git

Create a new branch for your contribution:

    git checkout -b feature/your-feature-name
Make your changes and ensure that the tests pass.

    python -m pytest tests

Update the [change log](./CHANGELOG.md) and the version number in [efootprint/\_\_init__.py](./efootprint/__init__.py)

Commit your changes with a clear and concise commit message, **and sign it using the -s or --signoff flag to declare that you adhere to the Developer Certificate of Origin (see below)**:

    git commit -s -m "Add your commit message here"
Push your changes to your forked repository:

    git push origin feature/your-feature-name
Create a pull request (PR) to the main branch of the e-footprint repository.

## Developer Certificate of Origin (DCO)
Contributions to this project require that you sign off on each commit to certify that you have the right to contribute the code.

For each commit, add a sign-off line to your commit message using the -s or --signoff flag:

    git commit -s -m "Your commit message here"
This will automatically add a "Signed-off-by: Your Name <your.email@example.com>" line at the end of your commit message.

By signing off on your commit, you acknowledge that you have the right to submit it under the project's license terms by making the [following statement](https://developercertificate.org/):

*By making a contribution to this project, I certify that:*

*(a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or*

*(b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or*

*(c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.*

*(d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.*

More info on the use of DCOs by the Linux Foundation at [https://wiki.linuxfoundation.org/dco](https://wiki.linuxfoundation.org/dco).

# Review Process
All contributions will be reviewed by project maintainers. During the review process, you may be asked to make additional changes to your code or documentation. Please be responsive to these requests and work collaboratively with the maintainers to address any feedback.

# Thank You
Thank you for considering contributing to e-footprint. Your contributions are valuable and help improve the project for everyone. We appreciate your efforts and look forward to working with you !

Happy coding 🚀

E-footprint Team
