# Power Dialer v0.1
&nbsp;

## Installation
 
#### 1. Install python 3.8
#### 2. Install pipenv
#### 3. Install local DynamoDB (keep the default port at 8000)
#### 4. Clone this project
#### 5. Give it a try by following [a manual test](manual_testing.md)

## To do

* Automated test script
* User Guide of APIs
* User Guide of integration
* Updated desgin documentation
* Add logging feature
* ...


## Design

### 1. AgentState data model
```
{
    agent_id,
    status, 
    cdc,
    latest_lead_phone_number,
    last_status,
    timestamp,
}
```

**Note:**
* `status` valid value: (`off`, `ready`, `in_call`, `inactive`)
* `cdc` = ***current dialing count***

&nbsp;
### 2. Matrix of Status, Event and Reaction 
| Status\Events |      login      | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dialing&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;call_fail&nbsp;&nbsp;&nbsp;&nbsp; |call_start | call_end | &nbsp;&nbsp;logout | keep_alive |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| `off` | *set `ready` and `cdc=0`*; *launch_dialing_event*| *raise warn* | *ignore* | *raise warn; end call* | *ignore* |  *ignore* | *ignore* |
| `ready` | *ignore* | *dial<br/>`DIAL_RATIO-cdc` number of leads in parellel; set `cdc= DIAL_RATIO`*| *set `cdc=cdc-1`;<br/>launch_dialing_event* | *set `in_call`*; update `latest_lead_phone_number`, `timestamp` | *ignore* | *set `off`* | *ignore* |
| `in_call` | *ignore* | *raise warn* | *ignore* | *raise warn; end call* | *set `ready`, `cdc`=0; launch_dialing_event* | *set `off`* | *compare time elapsed<br/>since `timestatmp` with `KEEP_ALIVE_INTERVAL`; set `inactive` or update `timestamp`*|
| `inactive` | *set `ready`*; *launch_dialing_event* | *ignroe* | *ignore* | *raise warn; end call* | *ignore* | *set `off`* | *set `off`*| 

**NOTE:** 
* `DIAL_RATIO` is configurable constant that defines the maximum number of parallel dialing for an agent
* `cdc` = ***concurrent dialing count***
* `keep_alive`: An agent can be `in_call` for long period of time; `keep_alive` event, `timestamp` in the state and the configuration item `KEEP_ALIVE_INTERVAL` are purposed to identify the liveness.
* `dialing` event will trigger the reaction that maximizes the concurrency of dialing up to `DIAL_RATIO`

&nbsp;
### 3. Implementation in pseudo code

#### 3.1 PowerDialerApp
&nbsp;
```
# PowerDialerApp is the wrapper class of the application.
# The application will start by initiating a PowerDialerApp object instance.
# This class should be implemented as a singleton.

import class PowerDialer
import class AgentState
import class Queue
import class Map

# The app instance is a global variable should be seen by all involved modules
app= null;

def class PowerDialerApp
    agent_power_dialer_map = Map.new()
    event_queue = Queue.new()
    
    def function init(self)
        global app;
        app= self;
        for agent_state in AgentState.get_all()
            # The app may restart from an abnormal exit. The persisted state can help
            add_power_dialer(agent_state.agent_id);
        end for;
        run_thread( function -> event_loop(self) );
    end;
    
    def function shutdown()
        event_queue.enque('stop');
        event_queue.destroy();
    end;
    
    def event_loop(self)
        event= event_queue.dequeue()
        case event of 
            {'add_agent_dialer', agent_id} -> on_add_agent_dialer(agent_id)
            {'delete_agent_dialer', agent_id} -> on_remove_agent_dialer(agent_id)
            'stop' ->
                return;
        end case
        event_loop(self)
    end;
        
    def function on_add_agent_dialer(agent_id)
        AgentState.create(agent_id);
        agent_power_dialer_map.add({agent_id, PowerDialer.new(agent_id)});
    end;
    
    def function on_delete_agent_dialer(self, dialer)
        AgentState.delete(agent_id);
        agent_power_dialer_map[agent_id].destroy();
        agent_power_dialer_map.delete(agent_id);
    end;
    
    def function add_agent_dialer(self, agent_id)
        event_queue.enqueue({'add_agent_dialer', agent_id);
    end;
    
    def function delete_agent_dialer(self, agent_id)
        event_queue.enqueue({'delete_agent_dialer', agent_id);
    end;
end
```
&nbsp;

#### 3.2 PowerDialer
&nbsp;
```

import class PowerDialerApp
import class AgentState
import class Queue

def class PowerDialer
    agent_id= null;
    state= null;
    event_queue= Queue.new(); 
    def function init(self, agent_id)
        self.agent_id= agent_id;
        self.state= AgentState.get(agent_id);
        run_thread( function-> event_loop(self) );
    end;
    
    def function shutdown()
        event_queue.enque('stop');
        event_queue.destroy();
    end;
    
    def event_loop(self)
        event = event_queue.dequeue()
        case event of 
            'login' -> on_agent_login()
            'dialing' -> on_dialing()
            'call_fail' -> on_call_failed()
            {'call_start', phone_number} -> on_call_started(phone_number)
            'call_end' -> on_call_ended()
            'stop' -> event_queue.destroy(); return;
            else -> nothing
        end
        event_loop(self);
    end
    
    def launch_dialing_event()
        event_queue.enqueue('dialing');
    end;
    
    def multi_thread_dialing(N)
        for i=0; i< N; i++
            run_thread( dial(agent_id, get_lead_phone_number_to_dial() )
        end;
    end;
    
    def update_state(new_state) 
        self.state= self.state.set(new_state);
        state.save();
    end;
        
    def on_agent_login()
        if self.state.status in ('off', 'inactive') 
            update_state({status: 'ready', cdc: 0, timestamp: now});
            launch_dialing_event();
        else
            nothing
        end;
    end;
    
    def on_dialing()
        case self.state.status 
            in ('off', 'in_call') ->
                raise_warn();
            'ready' ->
                cdc= self.state.cdc;
                update_state({cdc: DIAL_RATIO});
                multi_thread_dialing(DIAL_RATIO - cdc)
            else ->
                nothing;
        end
    end;
    
    def on_call_failed()
        case self.state.status
            'ready' ->
                update_state({cdc: cdc-1});
                launch_dialing_event();
            else ->
                nothing
        end
    end;
    
    def on_call_started(phone_number)
        case self.state.status
            'ready' ->
                update_state({status: 'in_call', latest_lead_phone_number: phone_number, timestatmp: now()});
            else ->
                raise_warn();
                end_call(phone_number);
        end;
    end;
    
    def on_call_ended()
        case self.state.status
            'in_call' ->
                update_state({status: 'ready', timestamp: now(), cdc: 0});
                launch_dialing_event();
            else ->
                nothing;
        end;
    end;
    
    def on_call_logout()
        case self.state.status
            'off' ->
                nothing;
            else ->
                update_state({status: 'off', timestamp: now());
        end;
    end;
    
    def on_keep_alive()
        case self.state.status 
            `inactive` ->
                update_state({status: 'off'})
            `in_call` ->
                if now()-self.state.timestamp > KEEP_ALIVE_INTERVAL 
                    update_state({status: 'inactive'))
                else
                    nothing;
                end;
            else ->
                nothing;
        end;
    end;
end
``` 
&nbsp;
#### 3.3 AgentState
&nbsp;
```
def class AgentState
    agent_id: null,
    status: null;
    cdc: null;
    latest_lead_phone_number: null;
    last_status: null;
    timestamp: null;
    
    def function init(agent_id)
        self.agent_id= agent_id;
        status= 'off';
        cdc= 0;
    end;

    def function create(agent_id)
        AgentState.new(agent_id).save();
    end;

    def function get(agent_id)
        select_from_db_table(agent_id);

    def function save(self)
        insert_into_db(self.all_attributes());
    end;
    
    def function delete(self)
        delete_from_db(self.agent_id);
    end;
end
```

