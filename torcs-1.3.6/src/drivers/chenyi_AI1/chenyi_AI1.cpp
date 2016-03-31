/***************************************************************************

    file                 : chenyi_AI1.cpp
    created              : 2014年 09月 01日 星期一 13:08:18 EDT
    copyright            : (C) 2002 Chenyi Chen

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#include <zmq.h>
#include <unistd.h>
// #include <zmq.hpp>
#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <iterator>
#include <cassert>

#ifdef _WIN32
#include <windows.h>
#endif

#include <stdio.h>
#include <stdlib.h> 
#include <string.h> 
#include <math.h>

#include <tgf.h> 
#include <track.h> 
#include <car.h> 
#include <raceman.h> 
#include <robottools.h>
#include <robot.h>

static tTrack	*curTrack;

static void initTrack(int index, tTrack* track, void *carHandle, void **carParmHandle, tSituation *s); 
static void newrace(int index, tCarElt* car, tSituation *s); 
static void drive(int index, tCarElt* car, tSituation *s); 
static void endrace(int index, tCarElt *car, tSituation *s);
static void shutdown(int index);
static int  InitFuncPt(int index, void *pt); 

void initTCLfilter(tCarElt* car);
float (*GET_DRIVEN_WHEEL_SPEED)(tCarElt* car);
float filterTCL_RWD(tCarElt* car);
float filterTCL_FWD(tCarElt* car);
float filterTCL_4WD(tCarElt* car);



/* 
 * Module entry point  
 */ 
extern "C" int 
chenyi_AI1(tModInfo *modInfo) 
{
    memset(modInfo, 0, 10*sizeof(tModInfo));

    modInfo->name    = strdup("chenyi_AI1");		/* name of the module (short) */
    modInfo->desc    = strdup("");	/* description of the module (can be long) */
    modInfo->fctInit = InitFuncPt;		/* init function */
    modInfo->gfId    = ROB_IDENT;		/* supported framework version */
    modInfo->index   = 1;

    return 0; 
} 

/* Module interface initialization. */
static int 
InitFuncPt(int index, void *pt) 
{ 
    tRobotItf *itf  = (tRobotItf *)pt; 

    itf->rbNewTrack = initTrack; /* Give the robot the track view called */ 
				 /* for every track change or new race */ 
    itf->rbNewRace  = newrace; 	 /* Start a new race */
    itf->rbDrive    = drive;	 /* Drive during race */
    itf->rbPitCmd   = NULL;
    itf->rbEndRace  = endrace;	 /* End of the current race */
    itf->rbShutdown = shutdown;	 /* Called before the module is unloaded */
    itf->index      = index; 	 /* Index used if multiple interfaces */
    return 0; 
} 

/* Called for every track change or new race. */
static void  
initTrack(int index, tTrack* track, void *carHandle, void **carParmHandle, tSituation *s) 
{ 
    curTrack = track;
    *carParmHandle = NULL; 
} 

/* Start a new race. */
void *context;
void *requester;
static void  
newrace(int index, tCarElt* car, tSituation *s) 
{ 
    // printf ("Connecting to server…\n");
    // context = zmq_ctx_new ();
    // requester = zmq_socket (context, ZMQ_REQ);
    // zmq_connect (requester, "tcp://localhost:5555");

    initTCLfilter(car);
} 


/* Antilocking filter for brakes */
const float ABS_SLIP = 0.9;        /* [-] range [0.95..0.3] */
const float ABS_MINSPEED = 3.0;    /* [m/s] */
float filterABS(tCarElt* car, float brake)
{
    if (car->_speed_x < ABS_MINSPEED) return brake;
    int i;
    float slip = 0.0;
    for (i = 0; i < 4; i++) {
        slip += car->_wheelSpinVel(i) * car->_wheelRadius(i) / car->_speed_x;
    }
    slip = slip/4.0;
    if (slip < ABS_SLIP) brake = brake*slip;
    return brake;
}


const float TCL_SLIP = 0.9;        /* [-] range [0.95..0.3] */
const float TCL_MINSPEED = 3.0;    /* [m/s] */
/* TCL filter for accelerator pedal */
float filterTCL(tCarElt* car, float accel)
{
    if (car->_speed_x < TCL_MINSPEED) return accel;
    float slip = car->_speed_x/(*GET_DRIVEN_WHEEL_SPEED)(car);
     if (slip < TCL_SLIP) {
        accel = 0.0;
    }
    return accel;
}
/* Traction Control (TCL) setup */
void initTCLfilter(tCarElt* car)
{
    const char *traintype = GfParmGetStr(car->_carHandle,
        SECT_DRIVETRAIN, PRM_TYPE, VAL_TRANS_RWD);
    if (strcmp(traintype, VAL_TRANS_RWD) == 0) {
        GET_DRIVEN_WHEEL_SPEED = &filterTCL_RWD;
    } else if (strcmp(traintype, VAL_TRANS_FWD) == 0) {
        GET_DRIVEN_WHEEL_SPEED = &filterTCL_FWD;
    } else if (strcmp(traintype, VAL_TRANS_4WD) == 0) {
        GET_DRIVEN_WHEEL_SPEED = &filterTCL_4WD;
    }
}

/* TCL filter plugin for rear wheel driven cars */
float filterTCL_RWD(tCarElt* car)
{
    return (car->_wheelSpinVel(REAR_RGT) + car->_wheelSpinVel(REAR_LFT)) *
            car->_wheelRadius(REAR_LFT) / 2.0;
}


/* TCL filter plugin for front wheel driven cars */
float filterTCL_FWD(tCarElt* car)
{
    return (car->_wheelSpinVel(FRNT_RGT) + car->_wheelSpinVel(FRNT_LFT)) *
            car->_wheelRadius(FRNT_LFT) / 2.0;
}


/* TCL filter plugin for all wheel driven cars */
float filterTCL_4WD(tCarElt* car)
{
    return (car->_wheelSpinVel(FRNT_RGT) + car->_wheelSpinVel(FRNT_LFT)) *
            car->_wheelRadius(FRNT_LFT) / 4.0 +
           (car->_wheelSpinVel(REAR_RGT) + car->_wheelSpinVel(REAR_LFT)) *
            car->_wheelRadius(REAR_LFT) / 4.0;
}


/* Compute gear. */
const float SHIFT = 0.85;         /* [-] (% of rpmredline) */
const float SHIFT_MARGIN = 4.0;  /* [m/s] */

int getGear(tCarElt *car)
{
	if (car->_gear <= 0)
		return 1;
	float gr_up = car->_gearRatio[car->_gear + car->_gearOffset];
	float omega = car->_enginerpmRedLine/gr_up;
	float wr = car->_wheelRadius(2);

	if (omega*wr*SHIFT < car->_speed_x) {
		return car->_gear + 1;
	} else {
		float gr_down = car->_gearRatio[car->_gear + car->_gearOffset - 1];
		omega = car->_enginerpmRedLine/gr_down;
		if (car->_gear > 1 && omega*wr*SHIFT > car->_speed_x + SHIFT_MARGIN) {
			return car->_gear - 1;
		}
	}
	return car->_gear;
}

//  Receive 0MQ string from socket and convert into C string
//  Caller must free returned string. Returns NULL if the context
//  is being terminated.
static char *
s_recv (void *socket) {
    char buffer [256];
    int size = zmq_recv (socket, buffer, 255, 0);
    if (size == -1)
        return NULL;
    if (size > 255)
        size = 255;
    buffer [size] = 0;
    return strdup (buffer);
}

//  Convert C string to 0MQ string and send to socket
static int
s_send (void *socket, const char *string) {
    int size = zmq_send (socket, string, strlen (string), 0);
    return size;
}

// Compute the length to the start of the segment.
float getDistToSegStart(tCarElt *ocar)
{
    if (ocar->_trkPos.seg->type == TR_STR) {
        return ocar->_trkPos.toStart;
    } else {
        return ocar->_trkPos.toStart*ocar->_trkPos.seg->radius;
    }
}

/* Drive during race. */
 
double initialSpeed;
bool setInitialSpeed = FALSE;
//double keepLR=-2.0;   // for two-lane
double desiredLane=-1;   // -1=left, 0=middle, 1=right
double laneWidth = 4.0;

static void drive(int index, tCarElt* car, tSituation *s) 
{ 
    ///// CHRIS

    // Send request
    const char *request;
    std::stringstream convert;
    float distance = s->cars[0]->_trkPos.seg->lgfromstart + getDistToSegStart(s->cars[0]) - car->_distFromStartLine;
    if (distance > curTrack->length/2.0f) {
        distance -= curTrack->length;
    } else if (distance < -curTrack->length/2.0f) {
        distance += curTrack->length;
    }
    // float speedCar0 = s->cars[0]->_speed_x;
    // float speedThisCar = car->_speed_x;
    // convert << speedCar0 << " " << speedThisCar << " " << distance;
    // request = convert.str().c_str();

    // s_send(requester, request);
    // // Retrieve result
    // char *result = s_recv(requester);
    // std::vector<float> v;
    // // Build an istream that holds the input string
    // std::istringstream iss(result);
    // // Iterate over the istream, using >> to grab floats
    // // and push_back to store them in the vector
    // std::copy(std::istream_iterator<float>(iss),
    //     std::istream_iterator<float>(),
    //     std::back_inserter(v));

    // // Put the result on standard out
    // // std::copy(v.begin(), v.end(),
    // //     std::ostream_iterator<float>(std::cout, ", "));
    // // std::cout << "\n";
    // car->info.brakeCollisionAvoidance = v[0];
    // car->info.steeringCollisionAvoidance = v[1];
    // std::cout << "brakes: " << car->info.brakeCollisionAvoidance  << " steering: " << car->info.steeringCollisionAvoidance << "\n";
    /////////

    memset(&car->ctrl, 0, sizeof(tCarCtrl));
    if (!setInitialSpeed) {
        initialSpeed = car->_speed_x;
    }

    if (car->info.steeringCollisionAvoidance > 0) {
        float angle;

        angle = RtTrackSideTgAngleL(&(car->_trkPos)) - car->_yaw;
        NORM_PI_PI(angle); // put the angle back in the range from -PI to PI
        angle -= car->info.steeringCollisionAvoidance*(car->_trkPos.toMiddle+desiredLane*laneWidth)/car->_trkPos.seg->width;

        // set up the values to return
        car->ctrl.steer = angle / car->_steerLock;
    }
    car->ctrl.gear = getGear(car);
    car->ctrl.brakeCmd=car->info.brakeCollisionAvoidance;
    // if (setInitialSpeed && car->info.brakeCollisionAvoidance == 0) {
    //     if (car->_speed_x > initialSpeed) {
    //        car->ctrl.brakeCmd=0.5;
    //        car->ctrl.accelCmd=0.0;
    //     }
    //     else if  (car->_speed_x < initialSpeed) {
    //        car->ctrl.accelCmd=0.5;
    //        car->ctrl.brakeCmd=0.0;
    //     }
    // }
    car->ctrl.accelCmd = filterTCL(car, car->ctrl.accelCmd);
    car->ctrl.brakeCmd = filterABS(car, car->ctrl.brakeCmd);

}

/* End of the current race */
static void
endrace(int index, tCarElt *car, tSituation *s)
{
    // zmq_close (requester);
    // zmq_ctx_destroy (context);
}

/* Called before the module is unloaded */
static void
shutdown(int index)
{
}

