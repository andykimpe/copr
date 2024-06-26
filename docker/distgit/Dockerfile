FROM registry.fedoraproject.org/fedora:39
MAINTAINER copr-devel@lists.fedorahosted.org

ARG ADDITIONAL_COPR_REPOSITORIES="goddabrouquita8280/copr-mock-testing"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux
ENV PYTHONPATH=/usr/share/copr/

# base packages
RUN set -ex ; \
    test -z "${ADDITIONAL_COPR_REPOSITORIES}" \
        || dnf -y install dnf-plugins-core \
        && for repo in $ADDITIONAL_COPR_REPOSITORIES ; do dnf -y copr enable $repo; done ; \
    dnf -y update && \
    dnf -y install htop \
                   which \
                   wget \
                   vim \
                   cgit \
                   python3-rpkg \
                   python3-ipdb \
                   tini \
    && dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-39.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-39.noarch.rpm -y \
    && dnf install mock-rpmfusion-nonfree -y \
    && sed -i 's|epel-9-x86_64.cfg|alma+epel-9-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-9-x86_64.cfg \
    && sed -i 's|epel-8-x86_64.cfg|alma+epel-8-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-8-x86_64.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_free.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_nonfree.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && sed -i 's|epel-next-9-x86_64.cfg|epel-next-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && sed -i 's|epel-next+rpmfusion_free-9-x86_64.cfg|epel-next+rpmfusion_free-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && dnf -y install copr-dist-git bind-utils \
    && dnf clean all

RUN rm /etc/httpd/conf.d/ssl.conf

RUN echo "AliasMatch \"/repo(/.*)/md5(/.*)\" \"/var/lib/dist-git/cache/lookaside\\$1\\$2\"" >> /etc/httpd/conf.d/dist-git/lookaside-copr.conf && \
    echo "Alias /repo/ /var/lib/dist-git/cache/lookaside/" >>  /etc/httpd/conf.d/dist-git/lookaside-copr.conf

RUN sed -i 's/Listen 80/Listen 5001/' /etc/httpd/conf/httpd.conf

RUN mkdir /tmp/copr-dist-git
RUN chown copr-dist-git:packager /tmp/copr-dist-git

# copy filesystem setup and setup ownership and permissions
COPY files/ /
RUN chmod 644 /etc/copr/copr-dist-git.conf

RUN echo " [user]" >> /home/copr-dist-git/.gitconfig && \
    echo " email = copr-devel@lists.fedorahosted.org" >> /home/copr-dist-git/.gitconfig && \
    echo " name = Copr dist git" >> /home/copr-dist-git/.gitconfig && \
    chown copr-dist-git:copr-dist-git /home/copr-dist-git/.gitconfig

RUN sed -i "s/^cache-size.*//" /etc/cgitrc
RUN echo 'scan-path=/var/lib/dist-git/git/rpms' | tee -a /etc/cgitrc

RUN directories="/etc/httpd /var/run/httpd /var/log/httpd /var/lib/dist-git /run/lock" ; \
    chown -R copr-dist-git:root $directories && \
    chmod -R g+rwX $directories

RUN sed -i 's|frontend|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr/copr-dist-git.conf

USER copr-dist-git

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-c", "mkdir -p /var/lib/dist-git/cache /var/lib/dist-git/git && exec /usr/bin/copr-run-dispatcher-dist-git imports"]
