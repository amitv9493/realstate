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

### Pending Tasks
   - make Lockbox one-to-one field and add text field for the location and other.
   - Add Feedback model
   - match with the sent UI and make sure that every field is there in the backend.
