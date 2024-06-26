FROM registry.fedoraproject.org/fedora:39
MAINTAINER copr-devel@lists.fedorahosted.org

ARG ADDITIONAL_COPR_REPOSITORIES="goddabrouquita8280/copr-mock-testing"

# TERM is to make the tito work in container, rhbz#1733043
ENV TERM=linux

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
                   python3-ipdb \
# builder packages
                   openssh-server \
                   fedora-packager \
                   mock \
                   mock-lvm \
                   createrepo \
                   yum-utils \
                   rsync \
                   openssh-clients \
                   rpm \
                   glib2 \
                   ca-certificates \
                   scl-utils-build \
                   ethtool \
    && dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-39.noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-39.noarch.rpm -y \
    && dnf install mock-rpmfusion-nonfree bind-utils -y \
    && sed -i 's|epel-9-x86_64.cfg|alma+epel-9-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-9-x86_64.cfg \
    && sed -i 's|epel-8-x86_64.cfg|alma+epel-8-x86_64.cfg|' /etc/mock/epel+rpmfusion_free-8-x86_64.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_free.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && cat /etc/mock/epel-next-9-x86_64-rpmfusion_nonfree.cfg > /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && sed -i 's|epel-next-9-x86_64.cfg|epel-next-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_free.cfg \
    && sed -i 's|epel-next+rpmfusion_free-9-x86_64.cfg|epel-next+rpmfusion_free-8-x86_64.cfg|' /etc/mock/epel-next-8-x86_64-rpmfusion_nonfree.cfg \
    && dnf -y install copr-builder \
    && dnf clean all

COPY files/ /

# needed to run sshd
RUN ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -q

# setup root user
RUN echo 'root:passwd' | chpasswd && \
    chmod 700 /root /root/.ssh && \
    touch /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys && \
    cat /root/.ssh/id_backend.pub >> /root/.ssh/authorized_keys

RUN sed -i 's|http://distgit-httpd:5001|http://'$(dig @resolver4.opendns.com myip.opendns.com +short -4)':5001|' /etc/copr-distgit-client/docker.ini
RUN sed -i 's|frontend|'$(dig @resolver4.opendns.com myip.opendns.com +short -4)'|' /etc/copr-rpmbuild/main.ini
RUN sed -i 's|http://distgit-httpd:5001|http://'$(dig @resolver4.opendns.com myip.opendns.com +short -4)':5001|' /etc/copr-rpmbuild/main.ini

RUN echo 'config_opts["use_nspawn"] = False' >> /etc/mock/site-defaults.cfg

CMD ["/usr/sbin/sshd", "-D"]
