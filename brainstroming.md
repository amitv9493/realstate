### Notification implementation
1. #### Idea (using redis queue)
    - will not have to wait for history creation.
    - faster
    - comlplex setup.

2. #### Idea (Without redis queue)
   - will need to wait for history creation.
   - slower
   - no setup required.

#### Action types (send to Frontend dev in small case)
   - ASSIGNED
   - REASSIGNED
   - STARTED
   - COMPLETED
   - CREATER_CANCELLED
   - ASSIGNER_CANCELLED
