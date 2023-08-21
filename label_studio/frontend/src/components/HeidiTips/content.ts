import { Tip } from "./types";

export const TipsCollection: Record<string, Tip[]> = {
  projectCreation: [{
    title: "Did you know?",
    content: "It’s easier to find the projects when you organize them into workspaces using Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/manage_projects#Create-workspaces-to-organize-projects",
      params: {
        experiment: "project_creation_tip",
        treatment: "find_and_manage_projects",
      },
    },
  }, {
    title: "Unlock faster access provisioning",
    content: "Streamline assigning staff to multiple projects by assigning them to workspaces in Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/manage_projects#Add-or-remove-members-to-a-workspace",
      params: {
        experiment: "project_creation_tip",
        treatment: "faster_provisioning",
      },
    },
  }, {
    title: "Did you know?",
    content: "Users with the Manager role can supervise a set of projects by assigning them to workspaces in Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/manage_users#Roles-in-Label-Studio-Enterprise",
      params: {
        experiment: "project_creation_tip",
        treatment: "supervise_projects",
      },
    },
  }, {
    title: "Did you know?",
    content: "You can control access to specific projects and workspaces for internal team members and external annotators using Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/manage_users#Roles-in-Label-Studio-Enterprise",
      params: {
        experiment: "project_creation_tip",
        treatment: "access_to_projects",
      },
    },
  }, {
    title: "Did you know?",
    content: "You can use or modify dozens or templates to configure your labeling UI, or create a custom configuration from scratch using simple XML-like tag.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://labelstud.io/guide/setup",
      params: {
        experiment: "project_creation_tip",
        treatment: "templates",
      },
    },
  }, {
    title: "Did you know?",
    content: "You can label tasks with collaborators by setting the minimum number of annotations to more than one. ",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://labelstud.io/guide/labeling#Label-with-collaborators",
      params: {
        experiment: "project_creation_tip",
        treatment: "label_with_collaborators",
      },
    }
  }],
  organizationPage: [{
    title: "It looks like your team is growing!",
    content: "Assign roles to your team using Label Studio Enterprise and control access to sensitive data at the project and workspace levels.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/manage_users#Roles-in-Label-Studio-Enterprise",
      params: {
        experiment: "organization_page_tip",
        treatment: "team_growing",
      },
    }
  }, {
    title: "Want to simplify and secure logging in?",
    content: "Enable Single-Sign On for your team using SAML, SCIM2 or LDAP with Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/auth_setup",
      params: {
        experiment: "organization_page_tip",
        treatment: "enable_sso",
      },
    }
  }, {
    title: "Want to improve your labeling team’s efficiency?",
    content: "Gain insight into your annotators’ productivity with project performance dashboards in Label Studio Enterprise.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/dashboards",
      params: {
        experiment: "organization_page_tip",
        treatment: "project_performance",
      },
    }
  }, {
    title: "Want to automate task distribution?",
    content: "Create rules, automate how tasks are distributed to annotators, and only show tasks assigned to each annotator in their view.",
    closable: true,
    link: {
      label: "Learn more",
      url: "https://docs.humansignal.com/guide/setup_project#Set-up-annotation-settings-for-your-project",
      params: {
        experiment: "organization_page_tip",
        treatment: "automate_distribution",
      },
    }
  }, {
    title: "Share knowledge with the community",
    content: "Have questions, or a tip to share with other Label Studio users. Join the community slack channel for the latest updates. ",
    closable: true,
    link: {
      label: "Join the community",
      url: "https://label-studio.slack.com",
      params: {
        experiment: "organization_page_tip",
        treatment: "share_knowledge",
      },
    }
  }, {
    title: "Did you know?",
    content: "Label Studio supports multiple points of integration with cloud storage, machine learning models, and popular tools to automate your machine learning pipeline.",
    closable: true,
    link: {
      label: "Check out the integrations directory",
      url: "https://labelstud.io/integrations/",
      params: {
        experiment: "organization_page_tip",
        treatment: "integration_points",
      },
    }
  }]
}
