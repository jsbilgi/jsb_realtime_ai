CREATE TABLE account.user_history_chat (
    user_id uuid,
    session_id uuid,
    chat_id uuid,
    revision int, /* revision number - when someone edits their question and asks again*/
    created_time timestamp,
    request text, /* user's raw question */
    response text, /* ansewr given back to user */
    api_request text, /*api request - likely includes prompt magic around user query, also all model params */
    api_response text, /*api response - full api response */
    created date,    
    PRIMARY KEY (user_id, session_id, chat_id, revision)
) WITH CLUSTERING ORDER BY (session_id DESC, chat_id DESC, created_time DESC);


CREATE TABLE account.user_sessions (
    user_id uuid,
    session_id uuid,
    sso_unique_id text, /* third party sso id , was using bubble on this before so it stored bubble internal account id*/
    created date,
    created_time timestamp,
    geo_json text, /*geo location info*/
    platform_json text, /*device info*/
    PRIMARY KEY (user_id, session_id)
) WITH CLUSTERING ORDER BY (session_id ASC);

CREATE CUSTOM INDEX user_session_sso_id_sai_idx ON account.user_sessions (sso_unique_id) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX user_session_date_sai_idx ON account.user_sessions (created) USING 'StorageAttachedIndex';


CREATE TABLE account.users (
    user_id uuid PRIMARY KEY,
    sso_unique_id text,
    created date,
    created_time timestamp,
    email text, /*email address which is used as the key to get chat history now*/
    password text /*password hash, currently not used since using sso */
);

CREATE CUSTOM INDEX user_sso_id_sai_idx ON account.users (sso_unique_id) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX user_date_sai_idx ON account.users (created) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX user_email_sai_idx ON account.users (email) USING 'StorageAttachedIndex';