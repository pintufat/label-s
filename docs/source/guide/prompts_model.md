---
title: Create a model
short: Create a model
tier: enterprise
type: guide
order: 0
order_enterprise: 228
meta_title: Create a model
meta_description: How to create a Prompts model
section: Prompts
date: 2024-06-11 16:53:16
---


## Prerequisites

* An OpenAI API key. 
* You need to have a project that meets the following criteria:
  * Text-based data set (meaning you are annotating text and not image or video files). 
  * The labeling configuration for the project must be set up to use single-class classification (`choice="single"`). 
  * You should have at least one task with a [ground truth annotation](quality#Define-ground-truth-annotations-for-a-project). Only tasks with a ground truth will be listed in the prompt interface. 

## API key

You can only specify one OpenAI API key per organization, and it only needs to be added once. 

Once added, it is automatically used for all new models. 

To remove the key, click **API Keys** in the upper right of the Prompts page. You'll have the option to remove the key and add a new one. 

## Create a model

From the Prompts page, click **Create Model** in the upper right and then complete the following fields:

<div class="noheader rowheader">

| | |
| --- | --- |
| Name | Enter a name for the prompt model. |
| Description | Enter a description for the prompt model.  |
| Type | Select the model type. At this time, we only support [text classification](prompts_overview#Text-classification). |
| Target Project| Select the project you want to use. The projects that are listed must have a text-based dataset (meaning you are labeling text, not images).<br><br>You must have access to the project. If you are in the Manager role, you need to be added to the project to have access. <br><br>If you don't see a project listed, then you do not have any eligible projects available. This is likely because the project is set up for multiple selection (e.g. `choice="multiple"`), is using a data type that isn't supported (video, audio), or you do not have access to the project.   |
| Model Classes | This list is generated from the labeling configuration of the target project. |

</div>

![Screenshot of the create model page](/images/prompts/model_create.png)