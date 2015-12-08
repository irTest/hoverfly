package main

import (
	"io/ioutil"
	"net/http"
	"testing"
)

func TestReconstructRequest(t *testing.T) {
	req, _ := http.NewRequest("GET", "http://example.com", nil)

	// changing payload so we don't have to call middleware
	request := requestDetails{
		Path:        "/random-path",
		Method:      "POST",
		Query:       "?foo=bar",
		Destination: "changed.destination.com",
	}
	payload := Payload{Request: request}

	c := NewConstructor(req, payload)
	newRequest := c.reconstructRequest()
	expect(t, newRequest.Method, "POST")
	expect(t, newRequest.URL.Path, "/random-path")
	expect(t, newRequest.Host, "changed.destination.com")
	expect(t, newRequest.URL.RawQuery, "?foo=bar")
}

func TestReconstructRequestBodyPayload(t *testing.T) {
	req, _ := http.NewRequest("GET", "http://example.com", nil)

	payload := Payload{}
	c := NewConstructor(req, payload)
	c.payload.Request.Method = "OPTIONS"
	c.payload.Request.Destination = "newdestination"
	c.payload.Request.Body = "new request body here"

	newRequest := c.reconstructRequest()

	expect(t, newRequest.Method, "OPTIONS")
	expect(t, newRequest.Host, "newdestination")

	body, err := ioutil.ReadAll(newRequest.Body)

	expect(t, err, nil)
	expect(t, string(body), "new request body here")
}
