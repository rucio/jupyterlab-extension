/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020-2021
 */

import React, { useState, useEffect } from 'react';
import { createUseStyles } from 'react-jss';
import { UploadJobListItem } from './UploadJobListItem';
import { HorizontalHeading } from '../HorizontalHeading';
import useInterval from '../../utils/useInterval';
import { FileUploadJob } from '../../types';
import { useStoreState } from 'pullstate';
import { UIStore } from '../../stores/UIStore';
import { actions } from '../../utils/Actions';

const useStyles = createUseStyles({
  container: {
    padding: '16px 0 16px 0'
  },
  messageContainer: {
    padding: '16px'
  }
});

type MyProps = {
  visible: boolean;
};
export const UploadsTab: React.FC<MyProps> = ({ visible }) => {
  const classes = useStyles();
  const activeInstance = useStoreState(UIStore, s => s.activeInstance);

  const [jobs, setJobs] = useState<FileUploadJob[]>([]);

  const loadJobs = () => {
    if (!activeInstance) {
      return;
    }

    actions
      .fetchUploadJobs(activeInstance.name)
      .then(jobs => setJobs(jobs))
      .catch(e => console.log(e));
  };

  useEffect(() => {
    if (visible) {
      loadJobs();
    }
  }, [activeInstance, visible]);

  useInterval(() => {
    if (visible) {
      loadJobs();
    }
  }, 5000);

  const onDelete = (id: string) => {
    if (!activeInstance) {
      return;
    }

    actions
      .deleteUploadJob(activeInstance.name, id)
      .then(() => {
        console.log('Job deleted');
        const newJobs = jobs.filter(j => j.id !== id);
        setJobs(newJobs);
      })
      .finally(() => {
        loadJobs();
      });
  };

  return (
    <div>
      {jobs.length > 0 && (
        <div className={classes.container}>
          <React.Fragment>
            <HorizontalHeading title="Upload Jobs" />
            {jobs.map(job => (
              <UploadJobListItem
                key={job.id}
                job={job}
                onDeleteClick={() => onDelete(job.id)}
              />
            ))}
          </React.Fragment>
        </div>
      )}
      {jobs.length === 0 && (
        <div className={classes.messageContainer}>
          You do not have upload jobs.
        </div>
      )}
    </div>
  );
};
