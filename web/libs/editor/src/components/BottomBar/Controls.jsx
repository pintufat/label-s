/**
 * This panel is used with FF_1170 + FF_3873 in new interface,
 * but it's also used in old interface with FF_3873, but without FF_1170.
 * Only this component should get interface updates, other versions should be removed.
 */

import { inject, observer } from "mobx-react";
import { Button } from "../../common/Button/Button";
import { Tooltip } from "../../common/Tooltip/Tooltip";
import { Block, cn, Elem } from "../../utils/bem";
import { isDefined } from "../../utils/utilities";
import { IconBan } from "../../assets/icons";
import { FF_REVIEWER_FLOW, isFF } from "../../utils/feature-flags";
import "./Controls.scss";
import { useCallback, useMemo, useState } from "react";
import { LsChevron } from "../../assets/icons";
import { Dropdown } from "../../common/Dropdown/DropdownComponent";

const TOOLTIP_DELAY = 0.8;

const ButtonTooltip = inject("store")(
  observer(({ store, title, children }) => {
    return (
      <Tooltip title={title} enabled={store.settings.enableTooltips} mouseEnterDelay={TOOLTIP_DELAY}>
        {children}
      </Tooltip>
    );
  }),
);

const controlsInjector = inject(({ store }) => {
  return {
    store,
    history: store?.annotationStore?.selected?.history,
  };
});

const CustomControl = observer(({ button }) => {
  const look = button.disabled ? "disabled" : button.look ?? "primary";
  const [waiting, setWaiting] = useState(false);
  const clickHandler = useCallback(
    async (e) => {
      setWaiting(true);
      await button.onClick(e, button);
      setWaiting(false);
    },
    [button, button.onClick],
  );
  return (
    <ButtonTooltip key={button.key} title={button.tooltip}>
      <Button
        aria-label={button.ariaLabel}
        disabled={button.disabled}
        look={look}
        onClick={clickHandler}
        waiting={waiting}
      >
        {button.title}
      </Button>
    </ButtonTooltip>
  );
});

export const CustomControls = controlsInjector(
  observer(({ store }) => {
    const buttons = store.controlButtons;
    return (
      <Block name="controls">
        {buttons.map((button) => (
          <CustomControl button={button} />
        ))}
      </Block>
    );
  }),
);

export const Controls = controlsInjector(
  observer(({ store, history, annotation }) => {
    const isReview = store.hasInterface("review") || annotation.canBeReviewed;
    const isNotQuickView = store.hasInterface("topbar:prevnext");
    const historySelected = isDefined(store.annotationStore.selectedHistory);
    const { userGenerate, sentUserGenerate, versions, results, editable: annotationEditable } = annotation;
    const dropdownTrigger = cn("dropdown").elem("trigger").toClassName();
    const buttons = [];

    const [isInProgress, setIsInProgress] = useState(false);
    const disabled = !annotationEditable || store.isSubmitting || historySelected || isInProgress;
    const submitDisabled = store.hasInterface("annotations:deny-empty") && results.length === 0;

    const buttonHandler = useCallback(
      async (e, callback, tooltipMessage) => {
        const { addedCommentThisSession, currentComment, commentFormSubmit } = store.commentStore;

        if (isInProgress) return;
        setIsInProgress(true);

        const selected = store.annotationStore?.selected;

        if (addedCommentThisSession) {
          selected?.submissionInProgress();
          callback();
        } else if (currentComment[annotation.id]?.trim()) {
          e.preventDefault();
          selected?.submissionInProgress();
          await commentFormSubmit();
          callback();
        } else {
          store.commentStore.setTooltipMessage(tooltipMessage);
        }
        setIsInProgress(false);
      },
      [
        store.rejectAnnotation,
        store.skipTask,
        store.commentStore.currentComment,
        store.commentStore.commentFormSubmit,
        store.commentStore.addedCommentThisSession,
        isInProgress,
      ],
    );

    const RejectButton = useMemo(() => {
      return (
        <ButtonTooltip key="reject" title="Reject annotation: [ Ctrl+Space ]">
          <Button
            aria-label="reject-annotation"
            disabled={disabled}
            onClick={async (e) => {
              if (store.hasInterface("comments:reject") ?? true) {
                buttonHandler(e, () => store.rejectAnnotation({}), "Please enter a comment before rejecting");
              } else {
                const selected = store.annotationStore?.selected;

                selected?.submissionInProgress();
                await store.commentStore.commentFormSubmit();
                store.rejectAnnotation({});
              }
            }}
          >
            Reject
          </Button>
        </ButtonTooltip>
      );
    }, [disabled, store]);

    if (isReview) {
      buttons.push(RejectButton);

      buttons.push(
        <ButtonTooltip key="accept" title="Accept annotation: [ Ctrl+Enter ]">
          <Button
            aria-label="accept-annotation"
            disabled={disabled}
            look="primary"
            onClick={async () => {
              const selected = store.annotationStore?.selected;

              selected?.submissionInProgress();
              await store.commentStore.commentFormSubmit();
              store.acceptAnnotation();
            }}
          >
            {history.canUndo ? "Fix + Accept" : "Accept"}
          </Button>
        </ButtonTooltip>,
      );
    } else if (annotation.skipped) {
      buttons.push(
        <Elem name="skipped-info" key="skipped">
          <IconBan color="#d00" /> Was skipped
        </Elem>,
      );
      buttons.push(
        <ButtonTooltip key="cancel-skip" title="Cancel skip: []">
          <Button
            aria-label="cancel-skip"
            disabled={disabled}
            look="primary"
            onClick={async () => {
              const selected = store.annotationStore?.selected;

              selected?.submissionInProgress();
              await store.commentStore.commentFormSubmit();
              store.unskipTask();
            }}
          >
            Cancel skip
          </Button>
        </ButtonTooltip>,
      );
    } else {
      if (store.hasInterface("skip")) {
        buttons.push(
          <ButtonTooltip key="skip" title="Cancel (skip) task: [ Ctrl+Space ]">
            <Button
              aria-label="skip-task"
              disabled={disabled}
              onClick={async (e) => {
                if (store.hasInterface("comments:skip") ?? true) {
                  buttonHandler(e, () => store.skipTask({}), "Please enter a comment before skipping");
                } else {
                  const selected = store.annotationStore?.selected;

                  selected?.submissionInProgress();
                  await store.commentStore.commentFormSubmit();
                  store.skipTask({});
                }
              }}
            >
              Skip
            </Button>
          </ButtonTooltip>,
        );
      }

      const isDisabled = disabled || submitDisabled;
      const look = isDisabled ? "disabled" : "primary";

      const useExitOption = !isDisabled && isNotQuickView;

      const SubmitOption = ({ isUpdate, onClickMethod }) => {
        return (
          <Button
            name="submit-option"
            look="secondary"
            onClick={async (event) => {
              event.preventDefault();

              const selected = store.annotationStore?.selected;

              selected?.submissionInProgress();

              if ("URLSearchParams" in window) {
                const searchParams = new URLSearchParams(window.location.search);

                searchParams.set("exitStream", "true");
                const newRelativePathQuery = `${window.location.pathname}?${searchParams.toString()}`;

                window.history.pushState(null, "", newRelativePathQuery);
              }

              await store.commentStore.commentFormSubmit();
              onClickMethod();
            }}
          >
            {`${isUpdate ? "Update" : "Submit"} and exit`}
          </Button>
        );
      };

      if (userGenerate || (store.explore && !userGenerate && store.hasInterface("submit"))) {
        const title = submitDisabled ? "Empty annotations denied in this project" : "Save results: [ Ctrl+Enter ]";

        buttons.push(
          <ButtonTooltip key="submit" title={title}>
            <Elem name="tooltip-wrapper">
              <Button
                aria-label="submit"
                name="submit"
                disabled={isDisabled}
                look={look}
                mod={{ has_icon: useExitOption, disabled: isDisabled }}
                onClick={async (event) => {
                  if (event.target.classList.contains(dropdownTrigger)) return;
                  const selected = store.annotationStore?.selected;

                  selected?.submissionInProgress();
                  await store.commentStore.commentFormSubmit();
                  store.submitAnnotation();
                }}
                icon={
                  useExitOption && (
                    <Dropdown.Trigger
                      alignment="top-right"
                      content={<SubmitOption onClickMethod={store.submitAnnotation} isUpdate={false} />}
                    >
                      <div>
                        <LsChevron />
                      </div>
                    </Dropdown.Trigger>
                  )
                }
              >
                Submit
              </Button>
            </Elem>
          </ButtonTooltip>,
        );
      }

      if ((userGenerate && sentUserGenerate) || (!userGenerate && store.hasInterface("update"))) {
        const isUpdate = isFF(FF_REVIEWER_FLOW) || sentUserGenerate || versions.result;
        // no changes were made over previously submitted version — no drafts, no pending changes
        const noChanges = isFF(FF_REVIEWER_FLOW) && !history.canUndo && !annotation.draftId;
        const isUpdateDisabled = isDisabled || noChanges;
        const button = (
          <ButtonTooltip key="update" title={noChanges ? "No changes were made" : "Update this task: [ Ctrl+Enter ]"}>
            <Button
              aria-label="submit"
              name="submit"
              disabled={isUpdateDisabled}
              look={look}
              mod={{ has_icon: useExitOption, disabled: isUpdateDisabled }}
              onClick={async (event) => {
                if (event.target.classList.contains(dropdownTrigger)) return;
                const selected = store.annotationStore?.selected;

                selected?.submissionInProgress();
                await store.commentStore.commentFormSubmit();
                store.updateAnnotation();
              }}
              icon={
                useExitOption && (
                  <Dropdown.Trigger
                    alignment="top-right"
                    content={<SubmitOption onClickMethod={store.updateAnnotation} isUpdate={isUpdate} />}
                  >
                    <div>
                      <LsChevron />
                    </div>
                  </Dropdown.Trigger>
                )
              }
            >
              {isUpdate ? "Update" : "Submit"}
            </Button>
          </ButtonTooltip>
        );

        buttons.push(button);
      }
    }

    return <Block name="controls">{buttons}</Block>;
  }),
);
